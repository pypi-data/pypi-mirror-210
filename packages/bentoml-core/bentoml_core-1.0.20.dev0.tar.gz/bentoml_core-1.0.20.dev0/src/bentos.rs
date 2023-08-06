use std::{fs::File, time::Duration};

use pyo3::prelude::*;
use tar;
use zstd;

fn handle_py_signals<
	T: Send + 'static,
	E: Send + 'static,
	F: FnMut() -> Result<T, E> + Send + 'static,
>(
	py: Python<'_>,
	f: F,
) -> PyResult<T>
where
	PyErr: From<E>,
{
	let thread = std::thread::spawn(f);
	loop {
		py.check_signals()?;
		if thread.is_finished() {
			return Ok(thread.join().unwrap()?);
		}
		std::thread::sleep(Duration::from_millis(500));
	}
}

// TODO: convert this to take tag once bento is moved to rust.
#[pyfunction]
pub fn pack_bento(py: Python<'_>, path: &str, name: &str) -> PyResult<String> {
	let out_path = format!("{}.bento", name);
	let out_file = File::create(&out_path)?;

	let mut tar = tar::Builder::new(zstd::Encoder::new(out_file, 3)?);

	let path = path.to_string();
	handle_py_signals(py, move || tar.append_dir_all("", &path))?;

	Ok(out_path)
}
