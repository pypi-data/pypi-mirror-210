use pyo3::{exceptions::PyException, prelude::*};

#[pyclass(extends=PyException,subclass)]
#[derive(Debug)]
pub struct BentoMLException {
	msg: String,
}

impl From<BentoMLException> for PyErr {
	fn from(err: BentoMLException) -> PyErr {
		PyErr::new::<BentoMLException, _>((err.msg,))
	}
}

#[pymethods]
impl BentoMLException {
	#[classattr]
	fn error_code() -> u32 {
		500
	}

	#[classattr]
	fn grpc_status() -> u32 {
		13
	}
}
