# EBglmnet: Empirical Bayesian Lasso and Elastic Net Methods for Generalized Linear Models

Anhui Huang | Ph.D. Electrical and Computer Engineering 

<https://scholar.google.com/citations?user=WhDMZEIAAAAJ&hl=en>

##
Provides empirical Bayesian lasso and elastic net algorithms for variable selection and effect estimation. Key features include sparse variable selection and effect estimation via generalized linear regression models, high dimensionality with p>>n, and significance test for nonzero effects. This package outperforms other popular methods such as lasso and elastic net methods in terms of power of detection, false discovery rate, and power of detecting grouping effects. Please reference its use as A Huang and D Liu (2016) <doi:10.1093/bioinformatics/btw143>.

## PyPI installation 
`EBglmnet` is available on PyPI:  https://pypi.org/project/EBglmnet/1.0/. Run command `pip install EBglmnet` to install 
from PyPI.

`test/` folder contains examples using data packed along with this package in `data/` folder. 
To run `test/` examples, clone this repo, and run from `test/` directory. 


## Documentation
The theory and background for EBglmnet can be found 
in my Ph.D dissertation (Huang A. 2014). A vignette is also available in the `doc/` folder in the package.  


## Configuration
This package was originally developed to leverage high performance computation with BLAS/Lapack package. To build the C/C++ code, the intel OneMKL library is 
specified in the package setup. 
- Install the free OneMKL package (https://www.intel.com/content/www/us/en/docs/oneapi/programming-guide/2023-0/intel-oneapi-math-kernel-library-onemkl.html)
- Check if your package is the same as in the setup.py file ('/opt/intel/oneapi/mkl/2023.1.0/include'). Update the file 
accordingly if it was installed in a different path.
- Intel MKL package is also available in conda intel channel. The dynamic loading library path will need to be updated if users choose to use `mkl-devel` conda package. 


## R package
An R package with similar implementation is also available at CRAN: https://cran.r-project.org/web/packages/EBglmnet/index.html

    
## Reference
<p>Huang A., Liu D., <br>
EBglmnet: a comprehensive R package for sparse generalized linear regression models <br>
Bioinformatics, Volume 37, Issue 11, 2016, Pages 1627–1629</p>
<p>Huang A., Xu S., and Cai X. (2015). <br>
Empirical Bayesian elastic net for multiple quantitative trait locus mapping.</a><br>
<em>Heredity</em>, Vol. 114(1), 107-115.</p>
<p>Huang A. <br>
Sparse Model Learning for Inferring Genotype and Phenotype Associations. <br>
Ph.D Dissertation, University of Miami, Coral Gables, FL, USA. 2014 </p>
<p>Huang A., Xu S., and Cai X. (2014a).<br>
Whole-genome quantitative trait locus mapping reveals major role of epistasis on yield of rice.</a><br>
<em>PLoS ONE</em>, Vol. 9(1) e87330.</p>
<p>Huang A., Martin E., Vance J., and Cai X. (2014b).<br>
Detecting genetic interactions in pathway-based genome-wide association studies.</a><br>
<em>Genetic Epidemiology</em>, 38(4), 300-309.</p>
<p> Huang A., Xu S., and Cai X. (2013). <br>
Empirical Bayesian LASSO-logistic regression for multiple binary trait locus mapping. </a><br>
<em>BMC Genetics</em>, 14(1),5.</p>
<p>Cai X., Huang A., and Xu S., (2011). <br>
Fast empirical Bayesian LASSO for multiple quantitative trait locus mapping. </a><br>
<em>BMC Bioinformatics</em>, 12(1),211.</p>