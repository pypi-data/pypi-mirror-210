#-
#include generaldefs.h
#include COREPREprocedures.h

#define NumParts "MM_NUMBER_OF_PARTICLES"
#define NumDiags "MM_NUMBER_OF_DIAGRAMS"
* max power of external momenta that we'll keep
#define Nmax "THENMAX"
* min inverse power of cutoff that is set to zero (equal to 3-maxdim)
#define LAMBDAINVERSEmax "THELAMBDAINVERSEMAX"

v p1, ... , p`NumParts', pol1, ... , pol`NumParts';

#do i=1,`NumDiags';
 S diags'i';
#enddo;
.global;

*>>>>>>>>
#$counter = 0;
*<<<<<<<<

#if `NumDiags'

#do i=1,`NumDiags';
G expr'i'= diags'i';
#enddo
.sort

#include FILE_WITH_DIAGRAMS.aux;


#include wcdimension.dat
id LAMBDA^`LAMBDAINVERSEmax' = 0;


#call doall(`NumParts',setlightmasses,`isnotEFT',`LoopOrder')

id LAMBDA = 1;
id LAMBDA^-1 = 1;
.sort

.store

G  amplPROCESS=expr1+...+expr`NumDiags';

#else
G amplPROCESS=0;

#endif

.sort


#call collectterms


#write <FILE_WITH_DIAGRAMS.out> "%X"
print +f;

.end
