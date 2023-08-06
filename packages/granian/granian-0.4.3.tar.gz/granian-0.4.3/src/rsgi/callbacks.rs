use pyo3::prelude::*;
use pyo3_asyncio::TaskLocals;
use tokio::sync::oneshot;

use crate::{
    callbacks::{
        CallbackWrapper,
        callback_impl_run,
        callback_impl_loop_run,
        callback_impl_loop_step,
        callback_impl_loop_wake,
        callback_impl_loop_err
    },
    runtime::RuntimeRef,
    ws::{HyperWebsocket, UpgradeData}
};
use super::{
    io::{RSGIHTTPProtocol as HTTPProtocol, RSGIWebsocketProtocol as WebsocketProtocol},
    types::{RSGIScope as Scope, PyResponse, PyResponseBytes}
};


#[pyclass]
pub(crate) struct CallbackRunnerHTTP {
    proto: Py<HTTPProtocol>,
    context: TaskLocals,
    cb: PyObject
}

impl CallbackRunnerHTTP {
    pub fn new(
        py: Python,
        cb: CallbackWrapper,
        proto: HTTPProtocol,
        scope: Scope
    ) -> Self {
        let pyproto = Py::new(py, proto).unwrap();
        Self {
            proto: pyproto.clone(),
            context: cb.context,
            cb: cb.callback.call1(py, (scope, pyproto)).unwrap()
        }
    }

    callback_impl_run!();
}

#[pymethods]
impl CallbackRunnerHTTP {
    fn _loop_task<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        CallbackTaskHTTP::new(py, self.cb.clone(), self.proto.clone(), self.context.clone())?.run(py)
    }
}

#[pyclass]
pub(crate) struct CallbackTaskHTTP {
    proto: Py<HTTPProtocol>,
    context: TaskLocals,
    pycontext: PyObject,
    cb: PyObject
}

impl CallbackTaskHTTP {
    pub fn new(
        py: Python,
        cb: PyObject,
        proto: Py<HTTPProtocol>,
        context: TaskLocals
    ) -> PyResult<Self> {
        let pyctx = context.context(py);
        Ok(Self { proto, context, pycontext: pyctx.call_method0(pyo3::intern!(py, "copy"))?.into(), cb })
    }

    fn done(&self, py: Python) {
        if let Ok(mut proto) = self.proto.as_ref(py).try_borrow_mut() {
            if let Some(tx) = proto.tx() {
                let _ = tx.send(
                    PyResponse::Bytes(PyResponseBytes::empty(500, Vec::new()))
                );
            }
        }
    }

    fn err(&self, py: Python) {
        log::warn!("Application callable raised an exception");
        self.done(py)
    }

    callback_impl_loop_run!();
    callback_impl_loop_err!();
}

#[pymethods]
impl CallbackTaskHTTP {
    fn _loop_step(pyself: PyRef<'_, Self>, py: Python) -> PyResult<()> {
        callback_impl_loop_step!(pyself, py)
    }

    fn _loop_wake(pyself: PyRef<'_, Self>, py: Python, fut: PyObject) -> PyResult<PyObject> {
        callback_impl_loop_wake!(pyself, py, fut)
    }
}

#[pyclass]
pub(crate) struct CallbackRunnerWebsocket {
    proto: Py<WebsocketProtocol>,
    context: TaskLocals,
    cb: PyObject
}

impl CallbackRunnerWebsocket {
    pub fn new(
        py: Python,
        cb: CallbackWrapper,
        proto: WebsocketProtocol,
        scope: Scope
    ) -> Self {
        let pyproto = Py::new(py, proto).unwrap();
        Self {
            proto: pyproto.clone(),
            context: cb.context,
            cb: cb.callback.call1(py, (scope, pyproto)).unwrap()
        }
    }

    callback_impl_run!();
}

#[pymethods]
impl CallbackRunnerWebsocket {
    fn _loop_task<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        CallbackTaskWebsocket::new(py, self.cb.clone(), self.proto.clone(), self.context.clone())?.run(py)
    }
}

#[pyclass]
pub(crate) struct CallbackTaskWebsocket {
    proto: Py<WebsocketProtocol>,
    context: TaskLocals,
    pycontext: PyObject,
    cb: PyObject
}

impl CallbackTaskWebsocket {
    pub fn new(
        py: Python,
        cb: PyObject,
        proto: Py<WebsocketProtocol>,
        context: TaskLocals
    ) -> PyResult<Self> {
        let pyctx = context.context(py);
        Ok(Self { proto, context, pycontext: pyctx.call_method0(pyo3::intern!(py, "copy"))?.into(), cb })
    }

    fn done(&self, py: Python) {
        if let Ok(mut proto) = self.proto.as_ref(py).try_borrow_mut() {
            if let (Some(tx), res) = proto.tx() {
                let _ = tx.send(res);
            }
        }
    }

    fn err(&self, py: Python) {
        log::warn!("Application callable raised an exception");
        self.done(py)
    }

    callback_impl_loop_run!();
    callback_impl_loop_err!();
}

#[pymethods]
impl CallbackTaskWebsocket {
    fn _loop_step(pyself: PyRef<'_, Self>, py: Python) -> PyResult<()> {
        callback_impl_loop_step!(pyself, py)
    }

    fn _loop_wake(pyself: PyRef<'_, Self>, py: Python, fut: PyObject) -> PyResult<PyObject> {
        callback_impl_loop_wake!(pyself, py, fut)
    }
}

pub(crate) fn call_rtb_http(
    cb: CallbackWrapper,
    rt: RuntimeRef,
    req: hyper::Request<hyper::Body>,
    scope: Scope
) -> oneshot::Receiver<PyResponse> {
    let (tx, rx) = oneshot::channel();
    let protocol = HTTPProtocol::new(rt, tx, req);

    Python::with_gil(|py| {
        let _ = CallbackRunnerHTTP::new(py, cb, protocol, scope).run(py);
    });

    rx
}

pub(crate) fn call_rtt_http(
    cb: CallbackWrapper,
    rt: RuntimeRef,
    req: hyper::Request<hyper::Body>,
    scope: Scope
) -> oneshot::Receiver<PyResponse> {
    let (tx, rx) = oneshot::channel();
    let protocol = HTTPProtocol::new(rt, tx, req);

    tokio::task::spawn_blocking(move || {
        Python::with_gil(|py| {
            let _ = CallbackRunnerHTTP::new(py, cb, protocol, scope).run(py);
        });
    });

    rx
}

pub(crate) fn call_rtb_ws(
    cb: CallbackWrapper,
    rt: RuntimeRef,
    ws: HyperWebsocket,
    upgrade: UpgradeData,
    scope: Scope
) -> oneshot::Receiver<(i32, bool)> {
    let (tx, rx) = oneshot::channel();
    let protocol = WebsocketProtocol::new(rt, tx, ws, upgrade);

    Python::with_gil(|py| {
        let _ = CallbackRunnerWebsocket::new(py, cb, protocol, scope).run(py);
    });

    rx
}

pub(crate) fn call_rtt_ws(
    cb: CallbackWrapper,
    rt: RuntimeRef,
    ws: HyperWebsocket,
    upgrade: UpgradeData,
    scope: Scope
) -> oneshot::Receiver<(i32, bool)> {
    let (tx, rx) = oneshot::channel();
    let protocol = WebsocketProtocol::new(rt, tx, ws, upgrade);

    tokio::task::spawn_blocking(move || {
        Python::with_gil(|py| {
            let _ = CallbackRunnerWebsocket::new(py, cb, protocol, scope).run(py);
        });
    });

    rx
}
