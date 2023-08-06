use industrial_robots::robot::FanucLrMate200id;
use industrial_robots::{try_convert, Isometry3, Matrix4, Vector3};

pub fn fanuc_with_joints(joints: Vec<f64>) -> FanucLrMate200id {
    // TODO: Decide if we should verify if there are at least six joints
    let mut robot = FanucLrMate200id::new();
    robot.set_joints(&joints);
    robot
}

pub fn to_mat4(py_list: Vec<f64>) -> Matrix4<f64> {
    let mut mat = Matrix4::zeros();
    for i in 0..4 {
        for j in 0..4 {
            mat[(i, j)] = py_list[i * 4 + j];
        }
    }
    mat
}

pub fn from_mat4(mat: Matrix4<f64>) -> Vec<f64> {
    let mut py_list = Vec::new();
    for i in 0..4 {
        for j in 0..4 {
            py_list.push(mat[(i, j)]);
        }
    }
    py_list
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn mat4_orders_correctly() {
        let test_list = vec![
            1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0,
        ];
        let mat = to_mat4(test_list);
        assert_eq!(mat[(0, 0)], 1.0);
        assert_eq!(mat[(0, 1)], 2.0);
        assert_eq!(mat[(0, 2)], 3.0);
        assert_eq!(mat[(0, 3)], 4.0);
        assert_eq!(mat[(1, 0)], 5.0);
        assert_eq!(mat[(1, 1)], 6.0);
        assert_eq!(mat[(1, 2)], 7.0);
        assert_eq!(mat[(1, 3)], 8.0);
        assert_eq!(mat[(2, 0)], 9.0);
        assert_eq!(mat[(2, 1)], 10.0);
        assert_eq!(mat[(2, 2)], 11.0);
        assert_eq!(mat[(2, 3)], 12.0);
        assert_eq!(mat[(3, 0)], 13.0);
        assert_eq!(mat[(3, 1)], 14.0);
        assert_eq!(mat[(3, 2)], 15.0);
        assert_eq!(mat[(3, 3)], 16.0);
    }
}
