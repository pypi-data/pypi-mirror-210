mod utility;

use industrial_robots::{try_convert, Isometry3};
use pyo3::prelude::*;
use pyo3::types::PyList;
use utility::{fanuc_with_joints, from_mat4, to_mat4};

#[pyfunction]
fn fanuc_fk(joints: Vec<f64>) -> PyResult<Vec<Vec<f64>>> {
    let robot = fanuc_with_joints(joints);
    let mut poses = Vec::new();
    for pose in robot.link_poses() {
        poses.push(from_mat4(pose.to_matrix()));
    }
    Ok(poses)
}

#[pyfunction]
fn fanuc_ik(target_pose: Vec<f64>, starting_joints: Vec<f64>) -> PyResult<Vec<f64>> {
    let robot = fanuc_with_joints(starting_joints);

    let pose = to_mat4(target_pose);
    let target: Isometry3<f64> = try_convert(pose).unwrap();

    if let Some(joints) = robot.find_joints(&target) {
        let py_list = joints.iter().map(|x| x.to_owned()).collect::<Vec<f64>>();
        Ok(py_list)
    } else {
        Err(pyo3::exceptions::PyValueError::new_err("No solution found"))
    }
}

#[pymodule]
fn py_industrial_robots(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fanuc_fk, m)?)?;
    m.add_function(wrap_pyfunction!(fanuc_ik, m)?)?;
    Ok(())
}
