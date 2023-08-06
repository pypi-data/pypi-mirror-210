use pyo3::prelude::*;
use base64::{Engine as _, engine::general_purpose};

#[pyfunction]
pub fn encode(orig: &str) -> PyResult<String> {
    let bytes = orig.as_bytes();
    let encoded_url = general_purpose::URL_SAFE_NO_PAD.encode(bytes);
    Ok(encoded_url.to_owned())
}
#[pyfunction]
pub fn decode(orig: &str) -> PyResult<String> {
    let bytes = orig.as_bytes();
    let decoded_bytes = general_purpose::URL_SAFE_NO_PAD.decode(bytes).unwrap();
    Ok(String::from_utf8(decoded_bytes).unwrap())
}

/// A Python module implemented in Rust.
#[pymodule]
fn urlsafe_base64_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encode, m)?)?;
    m.add_function(wrap_pyfunction!(decode, m)?)?;
    Ok(())
}