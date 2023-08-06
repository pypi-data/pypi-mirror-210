mod bentos;
mod exceptions;
mod tag;

use pyo3::prelude::*;

pub const BENTOML_VERSION: &str = env!("CARGO_PKG_VERSION");

#[pymodule]
fn bentoml_core(py: Python, m: &PyModule) -> PyResult<()> {
	m.add_class::<tag::Tag>()?;
	m.add_function(wrap_pyfunction!(tag::validate_tag_str, m)?)?;

	let exceptions_module = PyModule::new(py, "exceptions")?;
	exceptions_module.add(
		"BentoMLException",
		py.get_type::<exceptions::BentoMLException>(),
	)?;
	m.add_submodule(exceptions_module)?;

	let bentos_module = PyModule::new(py, "bentos")?;
	bentos_module.add_function(wrap_pyfunction!(bentos::pack_bento, bentos_module)?)?;
	m.add_submodule(bentos_module)?;

	Ok(())
}
