use geo::{ConcaveHull, MultiPoint};

use pyo3::prelude::*;

type Points = Vec<[f64; 2]>;


#[pymodule]
fn rconcave(_py: Python, m: &PyModule) -> PyResult<()> {
    /// Finds the concave path around the points, the concavity factor controlls how concave/jagged the result is.
    /// concavity=0 -> the uncomprimising concave path. 
    /// concavity=big num -> the convex path
    ///
    /// # args: 
    /// points: Vec<f64>[n, 2]
    /// concavity: f64
    ///
    /// returns points: Vec<f64>[m, 2]
    #[pyfn(m)]
    #[pyo3(text_signature = "(points, concavity, /)")]
    fn concave_hull(points: Points, concavity: f64 ) -> PyResult<Points> {
        let m_points: MultiPoint<f64> = points.into();

        let hull = m_points.concave_hull(concavity);
    
        let hull_points = hull.exterior().coords().skip(1).map(|c| [c.x, c.y]).collect();
        Ok(hull_points)
    }
    Ok(())
}
