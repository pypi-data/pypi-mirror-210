use pyo3::prelude::*;
extern crate nalgebra as na;
use na::{DVector, Vector3, OMatrix, Dyn, U3 };
use parry3d_f64::{shape::TriMesh, query::{Ray, RayCast}};

use rboolean::{Faces, Points, mesh2trimesh};


type _Normal = Vector3<f64>;
/// used to represent angle in radians
type _Normals = OMatrix<f64, Dyn, U3>;
type _Angles = DVector<f64>;


const RAD2DEG: f64 = 180.0 / std::f64::consts::PI;
// const DEG2RAD: f64 = std::f64::consts::PI / 180.0;


fn _normals2angles(normals: _Normals, ref_normal: _Normal) -> _Angles{
    let product = normals * ref_normal;
    product.map(|e| e.acos())
}

fn rads2degs(angles: _Angles) -> _Angles{
    angles.map(|e| RAD2DEG*e)
}

type Normal = [f64; 3];
/// used to represent angle in radians
type Normals = Vec<Normal>;
type Angles = Vec<f64>;
type Mask = Vec<bool>;


fn _overhangs(mesh: &TriMesh, dir: _Normal) -> Mask{
    let small: f64 = 0.01;
    let perturbation = dir * small;
     mesh.vertices()
        .iter()
        .map(|v| {
            let ray = Ray::new((*v) + perturbation , dir);
            mesh.intersects_local_ray(&ray, f64::INFINITY)
        })
        .collect()
}


#[pymodule]
fn rdraft(_py: Python, m: &PyModule) -> PyResult<()> {

    /// return mask: Vec<bool> of points indicating if the blocked by trifaces along normal
    #[pyfn(m)]
    #[pyo3(text_signature = "(points, tris, normal, /)")]
    fn overhangs(points: Points, tris: Faces, normal: Normal) -> PyResult<Mask> {
        let mesh = mesh2trimesh((points, tris));
        let res = _overhangs(&mesh, normal.into());
        Ok(res)
    }
    
    
    /// calculates angles in radians for normals compared to ref_normal
    ///
    /// warning: 
    /// It does **not** check if inputs are normalized nor does it normalize for you
    ///
    /// # args: 
    /// normals: Vec[r=n, c=3]
    /// normal: Vec[r=3]
    ///
    /// returns angles: Vec[r=n]
    #[pyfn(m)]
    #[pyo3(text_signature = "(normals, ref_normal, degrees, /)")]
    fn normals2angles(normals: Normals, ref_normal: Normal, degrees: bool) -> PyResult<Angles> {
        let _normals = _Normals::from_fn(normals.len(), |r, c| normals[r][c]);
        let _ref_normal = _Normal::from_row_slice(&ref_normal);
        let res = _normals2angles(_normals, _ref_normal);
        if degrees{
            return Ok(rads2degs(res).data.into())
        }
        Ok(res.data.into())
    }

    
    /// returns a mask: Vec<bool>
    #[pyfn(m)]
    #[pyo3(text_signature = "(normals, ref_normal, value, invert,/)")]
    fn draft_mask(normals: Normals, ref_normal: Normal, value: f64, invert:bool) -> PyResult<Mask> {
        let _normals = _Normals::from_fn(normals.len(), |r, c| normals[r][c]);
        let mut _ref_normal = _Normal::from_row_slice(&ref_normal);
        if invert {
            _ref_normal.neg_mut()
        }

        let res = _normals2angles(_normals, _ref_normal); 
        
        let mask =  res.map(|e| e < value);
        Ok(mask.data.into())
    }

    Ok(())
}
