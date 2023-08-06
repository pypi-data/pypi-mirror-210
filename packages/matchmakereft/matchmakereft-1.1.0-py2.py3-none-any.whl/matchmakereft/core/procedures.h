#procedure linearize()
*** Implement linearity of Mom and dotp
*** This works because gam with momenta does not contain gamma5 and has only three arguments
id Mom(itrick?, mu1?)=Mom(itrick, mu1 );
id dotp(itrick?, k1?)=dotp(itrick, k1 );
id dotp(k1?, itrick?)=dotp(k1, itrick );
.sort
#endprocedure

#procedure prepare()
id I^2=-1;
id p1?.k1?=dotp(p1,k1);
** Write deltas in a way that FORM understands (so that it can sum over indices)
** The range of the index is understoof from its name (a=1, 8; i=1,3; y=1, D; ...)
id gi(?a)=d_(?a);
****** Form d_ does strange things when more than two indices are contracted
**** We have to implement it ourselves
* Contract deltas with non-repeated indices
repeat;
id, once deltaFF(mu1?,mu2?!{mu1?})=replace_(mu2,mu1);
endrepeat;
** Now we can only have deltaFF(mu,mu) that we will replace at the
** end of the calculation taking into account if mu appears somewhere else
** in the expression or not

*** Extract momentum explicitly from gamma string
*** Extract the loop momentum explicitly for later tensor reduction
#do jf=1,200
id,once gam(?a, p1?, ?b) = Mom(p1, mugam'jf')*gam(?a, mugam'jf', ?b);
#enddo;
*** Now all gamma matrices should have only indices
#call linearize
#endprocedure

#procedure expandmomenta(setlightmasses,n)
** sSS counts powers of momenta
** sSSandm counts powers of momenta and light non-vanishing masses
** we will want to keep sSSandm below Nmax so that we can have m^2/M^2 corrections
** to dimension 4 operators but not to dimension 6
** We are now going to expand in powers of external momenta
*** Let's count powers of external momenta (p1 to p6) in the numerator
*** they can only appear in Mom or dotp in the numerator
#do jc=1,`n';
id Mom(p'jc',mu1?)=sSS*Mom(p'jc',mu1);
id dotp(p'jc',k1?)=sSS*dotp(p'jc',k1);
id dotp(k1?,p'jc')=sSS*dotp(k1,p'jc');
#enddo;
*** eliminate terms that already have more than Nmax power in the numerator
id sSS^('Nmax'+1)=0;
.sort
** Now we do the denominators
** Trick to separate the loop momentum from the external momenta
id prop(p1?,sSS?)=prop(p1,p1,sSS);
argument prop,2;
id k1=0;
endargument;
argument prop,1;
#do jc=1,`n';
id p'jc'=0;
#enddo
endargument;
* Make sure k1 always appears with a plus sign in propagators
id prop(-k1, p1?, [MM.s1]?) = prop(k1, -p1, [MM.s1]);
id prop(-k1, 0, [MM.s1]?) = prop(k1, 0, [MM.s1]);
* Eliminate the factors of external momenta and light non-vanishing masses in the denominators
* We do it recursively for efficiency
id [MM.s1]?`setlightmasses'=sSS*[MM.s1];
repeat;
* First for the heavy masses
id,once prop(k1,p1?,[MM.s1]?!`setlightmasses') = prop(k1,0,[MM.s1])*(1-(sSS^2*dotp(p1,p1)+2*sSS*dotp(k1,p1))*prop(k1,p1,[MM.s1]));
id,once prop(0,p1?,[MM.s1]?!`setlightmasses') = prop(0,0,[MM.s1])*(1-(sSS^2*dotp(p1,p1))*prop(0,p1,[MM.s1]));
* Now for the light masses
id,once prop(k1,p1?,[MM.s1]?`setlightmasses') = prop(k1,0,0)*(1-(sSS^2*dotp(p1,p1)+2*sSS*dotp(k1,p1)-sSS^2*[MM.s1]^2)*prop(k1,p1,[MM.s1]));
id,once prop(k1,0,[MM.s1]?`setlightmasses') = prop(k1,0,0)*(1-(-sSS^2*[MM.s1]^2)*prop(k1,0,[MM.s1]));
id,once sSS^('Nmax'+1)=0;
endrepeat;
id sSS*[MM.s1]?`setlightmasses'=[MM.s1];
* Once the external momenta are eliminated from the propagators we go
* back to standard notation
id prop(k1?,0,[MM.s1]?)=prop(k1,[MM.s1]);
id prop(0,0,[MM.s1]?)=prop(0,[MM.s1]);
.sort

*** We have to implement linearity of dotp again (we have introduced
*** with sum of vectors here again)
id dotp(itrick?, k1?)=dotp(itrick, k1 );
id dotp(k1?, itrick?)=dotp(k1, itrick );
.sort


* set to zero objects that are zero (but form does not know they are)
id prop(0,0)=0;
*** On-shell heavy propagator (at zero momentum)
id prop(0,[MM.s1]?)=-1/[MM.s1]^2;
.sort

*** momenta only appear as Mom(p,mu) or as dotp(p1,p2)
*** we write dotp explicitly in terms of Mom
*** we use k1 instead of p2 because for the tadpole only p1 is defined
#do jf=1,200
id,once dotp(p1?,k1?)=Mom(p1,mudotp'jf')*Mom(k1,mudotp'jf');
#enddo;
#endprocedure


#procedure tensorreduction()


*** Keep only even powers of k1
id Mom(k1,mu1?) = [MM.s1]*Mom(k1,mu1);
repeat;
id [MM.s1]^2=1;
endrepeat;
id [MM.s1]=0;

.sort

id Mom(k1,mu1?)^2=k1.k1;
.sort
*: new code for tensor reduction with arbitrary number of Mom(k1,mu?)
*: Tensor reduction (valid to leading order in [MM.epsi], den(a,b)=1/(a-b*[MM.epsi]))
*: putting all k^mu in one function
id once Mom(k1,mu?) = tenredcountK(mu);
repeat;
    id once Mom(k1,mu?)*tenredcountK(?mua) = tenredcountK(?mua,mu);
endrepeat;
*: splitting tenredcountK in what will become den * (k1.k1)^n * dd_(mu1,...)
id tenredcountK(?mu) = tenredcountK(nargs_(?mu)) * tenredtensorpart(?mu) * tenredgg(?mu);
*: computing k1.k1 powers
repeat;
id tenredtensorpart(mu1?,mu2?,?mua) = (k1.k1) * tenredtensorpart(?mua);
endrepeat;
id tenredtensorpart = 1;

*: killing odd terms (there should be none left, but just to be sure)
id tenredcountK(sSS?odd_) = 0;
*: preparing the den computation 
id tenredcountK(sSS?) = den(tenredfden0(sSS),tenredfden1(sSS));
.sort
*: for '2n' indices, the denominator is D*(D+2)*(D+4)*...*(D+2*n-2)
*: which, expanded in [MM.epsi] is 
*: tenredfden0 - tenredfden1 * [MM.epsi] + O([MM.epsi]^2)
*: with 
*: tenredfden0 = 2^n Gamma(2+n)
*: tenredfden1 = 2^n Gamma(2+n) * (H(1+n)-1)
*: and H(x) = 1 + 1/2 + 1/3 + ... + 1/x  (the Harmonic number)
argument den;
    id tenredfden0(sSS?) = 2^(sSS/2)*fac_(2+sSS/2 -1);
    id tenredfden1(sSS?) = -(1-sum_(tenredj,1,sSS/2+1,1/tenredj))*fac_(2+sSS/2-1)*(2^(sSS/2));
endargument;
.sort
*: important to set tenredgg -> dd_ *after* the .sort command
id tenredgg(?mu) = dd_(?mu);
.sort


#endprocedure

*****************************************************************
****
****     Here comes the gamma matrices
****
*****************************************************************
#procedure newjoingammas()

** This will be used for the order of the chain
id uspin?spins(p1?,y1?)=INDSPIN(y1)*uspin(p1,y1);
repeat;
id disorder INDSPIN(y1?)*INDSPIN(y2?)=INDSPIN(y2)*INDSPIN(y1);
endrepeat;
chainin INDSPIN;
transform,INDSPIN,reverse(first,last);


id gam(y1?,?a, y2?)=gam(1,y1,?a, y2);

repeat;

id gam(ct1?,y1?,?a, y2?)*gam(ct2?,y2?, ?b)= gam(ct1+ct2,y1,?a, ?b);
id gam(ct1?,y1?,?a, y2?)*gam(ct2?,y3?,?b,y2?)=(-1)^ct2*gam(ct1+ct2,y1,?a, flipped(?b),y3);
id gam(ct1?,y1?,?a, y2?)*gam(ct2?,y1?,?b,y3?)=(-1)^ct1*gam(ct1+ct2,y2,flipped(?a),?b,y3);

endrepeat;


id gam(ct1?,y1?,?a, y2?)=gam(y1,?a, y2);


repeat;

id vbspin(p1?,y1?)*gam(y2?,?a,y1?)*uspin(k1?,y2?)=-vbspin(p1,y1)*gam(y1,flipped(?a),y2)*uspin(k1,y2);
id INDSPIN(?a,y2?,?b,y1?,?c)*uspin(p1?,y1?)*gam(y1?,?d,y2?)*uspin(k1?,y2?)=-INDSPIN(?a,y2,?b,y1,?c)*vbspin(k1,y2)*gam(y2,flipped(?d),y1)*uspin(p1,y1);
id INDSPIN(?a,y2?,?b,y1?,?c)*vbspin(p1?,y1?)*gam(y1?,?d,y2?)*vbspin(k1?,y2?)=-INDSPIN(?a,y2,?b,y1,?c)*vbspin(k1,y2)*gam(y2,flipped(?d),y1)*uspin(p1,y1);


endrepeat;


id INDSPIN(?a)=1;

argument gam;
id flipped()=flipped(gap);
endargument;


#endprocedure


#procedure flipgammas()


*This gets rid of flipped^n reversing the elements
*Now there are only 'first level' flips
repeat;
id, once
gam(?a,flipped(?b,flipped(?c),?d),?e)=gam(?a,flipped(?d),?c,flipped(?b),?e);
endrepeat;


argument gam;
id flipped=flipped(gap);
transform,flipped,reverse(first,last);
chainout flipped;


*Now all the elements are reversed, only need the signs

* when an index appears in an id it replaces indices and vectors
id flipped(mu?)=-flipped(mu);

id flipped(gap)=flipped();

chainin flipped;

endargument;


repeat;
* now we take the sign out
id gam(?a,-flipped(?b),?c)=-gam(?a,?b,?c);
* and eliminate flipped (gammas have already been flipped)
id gam(?a,flipped(?b),?c)=gam(?a,?b,?c);
endrepeat;


#endprocedure



#procedure dogammas(n,isnoteft)
*********************
* Join gamma lines in right order
*>>>>>>>>

repeat;
id,once gam(y1?,?a, y2?)*gam(y2?, ?b)= gam(y1,?a, ?b);
endrepeat;

*: new gamma lines ordering
*: we start the trace from the Lorentz index of an external boson if there is one
*: we start looking for Evect(p1,mu), and if not found, we proceed to p2,p3,p4
#do ixxx=1,`n'
if (count([MM.s1],1) == 0);
id,once Evect(p'ixxx',mu?)*gam(y1?,?a,mu?,?b, y1?) = [MM.s1] * Evect(p'ixxx',mu)*gam(y1,mu,?b, ?a,y1);
endif;
#enddo
.sort

id [MM.s1] = 1;

*<<<<<<<<


** Anticommute gamma5 and use gamma5^2=1 to take it to the left
repeat;
id,once gam(y1? , ?a, SIX, SEVEN, ?b) =0;
id,once gam(y1? , ?a, SEVEN, SIX, ?b) =0;
id,once gam(y1? , ?a, SIX, SIX, ?b) = 2*gam(y1 , ?a, SIX, ?b);
id,once gam(y1? , ?a, SEVEN, SEVEN, ?b) = 2*gam(y1 , ?a, SEVEN, ?b);
id,once gam(y1?, ?a, mu1?, SIX, ?b) =gam(y1,?a,SEVEN, mu1, ?b);
id,once gam(y1?, ?a, mu1?, SEVEN, ?b) =gam(y1,?a,SIX, mu1, ?b);
endrepeat;
.sort

** Now that we have all gamma5 to the left, let's write it explicitely
id gam(?a, SIX, ?b)= gam(?a, ?b)+gam(?a, FIVE, ?b);
id gam(?a, SEVEN, ?b)= gam(?a, ?b)-gam(?a, FIVE, ?b);



* Let us now eliminate repeated indices, we do it in all terms (open, closed, with or without gamma5)
* Terms without gamma5 are treated ok by form
*>>>>>>>>
b gam;
.sort
*: this puts everything apart from gam() in a function called bracket1. Its contents are not looked upon
*: until we release them explicitly
Collect bracket1;
*<<<<<<<<

repeat;

*>>>>>>>>
*: we only modify traces with a FIVE (note that we select gam(y1?,FIVE,...,y1?), with the same y1 index)
id gam(y1?,FIVE,?a,mua?,mua?,?b,y1?) = gam(y1,FIVE, ?a, ?b, y1) * D ;
*<<<<<<<<

id gam(y1?, ?a, mua?, mua?, ?b, y2?)= D*gam(y1, ?a, ?b, y2);
id,once gam(y1?, ?a, mua?, mu1?, ?b, mua?, ?c, y2?) =  - gam(y1, ?a, mu1, mua, ?b, mua, ?c, y2)+2*gam(y1, ?a, ?b, mu1, ?c, y2);
endrepeat;



id gam(y1?,FIVE,y1?) = 0;
id gam(y1?,FIVE,mu1?,mu2?,y1?) = 0;
id gam(y1?,FIVE, mu1?,y1?) = 0;
id gam(y1?,FIVE,mu1?,mu2?,mu3?,y1?) = 0;
id gam(y1?,FIVE,mu1?,mu2?,mu3?,mu4?,mu5?,y1?) = 0;


* Statement about gamma5 and e_ in form (with euclidean metric)
* We use our own gamma5 so we don't need to do anything about it
* we call epsM(mu,nu,rho,sigma) the minkowskian one
* in order to be able to use the euclidean one in form we define eps=I e_
* This changes the sign for contractions of 2 eps as it should and it is homogeneous for an odd number
* -------> >   Tr((gmu gnu grho gsigma) x g5) = -4i \eps(mu,nu,rho,sigma)   <-------
* JSP *
id gam(y1?,FIVE,mu1?,mu2?,mu3?,mu4?,y1?) = -4*I*epsM(mu1,mu2,mu3,mu4);


id gam(y1?,FIVE,mu1?,mu2?,mu3?,mu4?,mu5?,mu6?,y1?) = 
       - 4*epsM(mu1,mu2,mu3,mu4)*d_(mu5,mu6)*I
       + 4*epsM(mu1,mu2,mu3,mu5)*d_(mu4,mu6)*I
       - 4*epsM(mu1,mu2,mu3,mu6)*d_(mu4,mu5)*I
       - 4*epsM(mu1,mu2,mu4,mu5)*d_(mu3,mu6)*I
       + 4*epsM(mu1,mu2,mu4,mu6)*d_(mu3,mu5)*I
       - 4*epsM(mu1,mu2,mu5,mu6)*d_(mu3,mu4)*I
       + 4*epsM(mu1,mu3,mu4,mu5)*d_(mu2,mu6)*I
       - 4*epsM(mu1,mu3,mu4,mu6)*d_(mu2,mu5)*I
       + 4*epsM(mu1,mu3,mu5,mu6)*d_(mu2,mu4)*I
       - 4*epsM(mu1,mu4,mu5,mu6)*d_(mu2,mu3)*I
       - 4*epsM(mu2,mu3,mu4,mu5)*d_(mu1,mu6)*I
       + 4*epsM(mu2,mu3,mu4,mu6)*d_(mu1,mu5)*I
       - 4*epsM(mu2,mu3,mu5,mu6)*d_(mu1,mu4)*I
       + 4*epsM(mu2,mu4,mu5,mu6)*d_(mu1,mu3)*I
       - 4*epsM(mu3,mu4,mu5,mu6)*d_(mu1,mu2)*I
      ;

id gam(y1?,FIVE,mu1?,mu2?,mu3?,mu4?,mu5?,mu6?,mu7?,mu8?,y1?) = 
       - 4*epsM(mu1,mu2,mu3,mu4)*d_(mu5,mu6)*d_(mu7,mu8)*I
       + 4*epsM(mu1,mu2,mu3,mu4)*d_(mu5,mu7)*d_(mu6,mu8)*I
       - 4*epsM(mu1,mu2,mu3,mu4)*d_(mu5,mu8)*d_(mu6,mu7)*I
       + 4*epsM(mu1,mu2,mu3,mu5)*d_(mu4,mu6)*d_(mu7,mu8)*I
       - 4*epsM(mu1,mu2,mu3,mu5)*d_(mu4,mu7)*d_(mu6,mu8)*I
       + 4*epsM(mu1,mu2,mu3,mu5)*d_(mu4,mu8)*d_(mu6,mu7)*I
       - 4*epsM(mu1,mu2,mu3,mu6)*d_(mu4,mu5)*d_(mu7,mu8)*I
       + 4*epsM(mu1,mu2,mu3,mu6)*d_(mu4,mu7)*d_(mu5,mu8)*I
       - 4*epsM(mu1,mu2,mu3,mu6)*d_(mu4,mu8)*d_(mu5,mu7)*I
       + 4*epsM(mu1,mu2,mu3,mu7)*d_(mu4,mu5)*d_(mu6,mu8)*I
       - 4*epsM(mu1,mu2,mu3,mu7)*d_(mu4,mu6)*d_(mu5,mu8)*I
       + 4*epsM(mu1,mu2,mu3,mu7)*d_(mu4,mu8)*d_(mu5,mu6)*I
       - 4*epsM(mu1,mu2,mu3,mu8)*d_(mu4,mu5)*d_(mu6,mu7)*I
       + 4*epsM(mu1,mu2,mu3,mu8)*d_(mu4,mu6)*d_(mu5,mu7)*I
       - 4*epsM(mu1,mu2,mu3,mu8)*d_(mu4,mu7)*d_(mu5,mu6)*I
       - 4*epsM(mu1,mu2,mu4,mu5)*d_(mu3,mu6)*d_(mu7,mu8)*I
       + 4*epsM(mu1,mu2,mu4,mu5)*d_(mu3,mu7)*d_(mu6,mu8)*I
       - 4*epsM(mu1,mu2,mu4,mu5)*d_(mu3,mu8)*d_(mu6,mu7)*I
       + 4*epsM(mu1,mu2,mu4,mu6)*d_(mu3,mu5)*d_(mu7,mu8)*I
       - 4*epsM(mu1,mu2,mu4,mu6)*d_(mu3,mu7)*d_(mu5,mu8)*I
       + 4*epsM(mu1,mu2,mu4,mu6)*d_(mu3,mu8)*d_(mu5,mu7)*I
       - 4*epsM(mu1,mu2,mu4,mu7)*d_(mu3,mu5)*d_(mu6,mu8)*I
       + 4*epsM(mu1,mu2,mu4,mu7)*d_(mu3,mu6)*d_(mu5,mu8)*I
       - 4*epsM(mu1,mu2,mu4,mu7)*d_(mu3,mu8)*d_(mu5,mu6)*I
       + 4*epsM(mu1,mu2,mu4,mu8)*d_(mu3,mu5)*d_(mu6,mu7)*I
       - 4*epsM(mu1,mu2,mu4,mu8)*d_(mu3,mu6)*d_(mu5,mu7)*I
       + 4*epsM(mu1,mu2,mu4,mu8)*d_(mu3,mu7)*d_(mu5,mu6)*I
       - 4*epsM(mu1,mu2,mu5,mu6)*d_(mu3,mu4)*d_(mu7,mu8)*I
       + 4*epsM(mu1,mu2,mu5,mu6)*d_(mu3,mu7)*d_(mu4,mu8)*I
       - 4*epsM(mu1,mu2,mu5,mu6)*d_(mu3,mu8)*d_(mu4,mu7)*I
       + 4*epsM(mu1,mu2,mu5,mu7)*d_(mu3,mu4)*d_(mu6,mu8)*I
       - 4*epsM(mu1,mu2,mu5,mu7)*d_(mu3,mu6)*d_(mu4,mu8)*I
       + 4*epsM(mu1,mu2,mu5,mu7)*d_(mu3,mu8)*d_(mu4,mu6)*I
       - 4*epsM(mu1,mu2,mu5,mu8)*d_(mu3,mu4)*d_(mu6,mu7)*I
       + 4*epsM(mu1,mu2,mu5,mu8)*d_(mu3,mu6)*d_(mu4,mu7)*I
       - 4*epsM(mu1,mu2,mu5,mu8)*d_(mu3,mu7)*d_(mu4,mu6)*I
       - 4*epsM(mu1,mu2,mu6,mu7)*d_(mu3,mu4)*d_(mu5,mu8)*I
       + 4*epsM(mu1,mu2,mu6,mu7)*d_(mu3,mu5)*d_(mu4,mu8)*I
       - 4*epsM(mu1,mu2,mu6,mu7)*d_(mu3,mu8)*d_(mu4,mu5)*I
       + 4*epsM(mu1,mu2,mu6,mu8)*d_(mu3,mu4)*d_(mu5,mu7)*I
       - 4*epsM(mu1,mu2,mu6,mu8)*d_(mu3,mu5)*d_(mu4,mu7)*I
       + 4*epsM(mu1,mu2,mu6,mu8)*d_(mu3,mu7)*d_(mu4,mu5)*I
       - 4*epsM(mu1,mu2,mu7,mu8)*d_(mu3,mu4)*d_(mu5,mu6)*I
       + 4*epsM(mu1,mu2,mu7,mu8)*d_(mu3,mu5)*d_(mu4,mu6)*I
       - 4*epsM(mu1,mu2,mu7,mu8)*d_(mu3,mu6)*d_(mu4,mu5)*I
       + 4*epsM(mu1,mu3,mu4,mu5)*d_(mu2,mu6)*d_(mu7,mu8)*I
       - 4*epsM(mu1,mu3,mu4,mu5)*d_(mu2,mu7)*d_(mu6,mu8)*I
       + 4*epsM(mu1,mu3,mu4,mu5)*d_(mu2,mu8)*d_(mu6,mu7)*I
       - 4*epsM(mu1,mu3,mu4,mu6)*d_(mu2,mu5)*d_(mu7,mu8)*I
       + 4*epsM(mu1,mu3,mu4,mu6)*d_(mu2,mu7)*d_(mu5,mu8)*I
       - 4*epsM(mu1,mu3,mu4,mu6)*d_(mu2,mu8)*d_(mu5,mu7)*I
       + 4*epsM(mu1,mu3,mu4,mu7)*d_(mu2,mu5)*d_(mu6,mu8)*I
       - 4*epsM(mu1,mu3,mu4,mu7)*d_(mu2,mu6)*d_(mu5,mu8)*I
       + 4*epsM(mu1,mu3,mu4,mu7)*d_(mu2,mu8)*d_(mu5,mu6)*I
       - 4*epsM(mu1,mu3,mu4,mu8)*d_(mu2,mu5)*d_(mu6,mu7)*I
       + 4*epsM(mu1,mu3,mu4,mu8)*d_(mu2,mu6)*d_(mu5,mu7)*I
       - 4*epsM(mu1,mu3,mu4,mu8)*d_(mu2,mu7)*d_(mu5,mu6)*I
       + 4*epsM(mu1,mu3,mu5,mu6)*d_(mu2,mu4)*d_(mu7,mu8)*I
       - 4*epsM(mu1,mu3,mu5,mu6)*d_(mu2,mu7)*d_(mu4,mu8)*I
       + 4*epsM(mu1,mu3,mu5,mu6)*d_(mu2,mu8)*d_(mu4,mu7)*I
       - 4*epsM(mu1,mu3,mu5,mu7)*d_(mu2,mu4)*d_(mu6,mu8)*I
       + 4*epsM(mu1,mu3,mu5,mu7)*d_(mu2,mu6)*d_(mu4,mu8)*I
       - 4*epsM(mu1,mu3,mu5,mu7)*d_(mu2,mu8)*d_(mu4,mu6)*I
       + 4*epsM(mu1,mu3,mu5,mu8)*d_(mu2,mu4)*d_(mu6,mu7)*I
       - 4*epsM(mu1,mu3,mu5,mu8)*d_(mu2,mu6)*d_(mu4,mu7)*I
       + 4*epsM(mu1,mu3,mu5,mu8)*d_(mu2,mu7)*d_(mu4,mu6)*I
       + 4*epsM(mu1,mu3,mu6,mu7)*d_(mu2,mu4)*d_(mu5,mu8)*I
       - 4*epsM(mu1,mu3,mu6,mu7)*d_(mu2,mu5)*d_(mu4,mu8)*I
       + 4*epsM(mu1,mu3,mu6,mu7)*d_(mu2,mu8)*d_(mu4,mu5)*I
       - 4*epsM(mu1,mu3,mu6,mu8)*d_(mu2,mu4)*d_(mu5,mu7)*I
       + 4*epsM(mu1,mu3,mu6,mu8)*d_(mu2,mu5)*d_(mu4,mu7)*I
       - 4*epsM(mu1,mu3,mu6,mu8)*d_(mu2,mu7)*d_(mu4,mu5)*I
       + 4*epsM(mu1,mu3,mu7,mu8)*d_(mu2,mu4)*d_(mu5,mu6)*I
       - 4*epsM(mu1,mu3,mu7,mu8)*d_(mu2,mu5)*d_(mu4,mu6)*I
       + 4*epsM(mu1,mu3,mu7,mu8)*d_(mu2,mu6)*d_(mu4,mu5)*I
       - 4*epsM(mu1,mu4,mu5,mu6)*d_(mu2,mu3)*d_(mu7,mu8)*I
       + 4*epsM(mu1,mu4,mu5,mu6)*d_(mu2,mu7)*d_(mu3,mu8)*I
       - 4*epsM(mu1,mu4,mu5,mu6)*d_(mu2,mu8)*d_(mu3,mu7)*I
       + 4*epsM(mu1,mu4,mu5,mu7)*d_(mu2,mu3)*d_(mu6,mu8)*I
       - 4*epsM(mu1,mu4,mu5,mu7)*d_(mu2,mu6)*d_(mu3,mu8)*I
       + 4*epsM(mu1,mu4,mu5,mu7)*d_(mu2,mu8)*d_(mu3,mu6)*I
       - 4*epsM(mu1,mu4,mu5,mu8)*d_(mu2,mu3)*d_(mu6,mu7)*I
       + 4*epsM(mu1,mu4,mu5,mu8)*d_(mu2,mu6)*d_(mu3,mu7)*I
       - 4*epsM(mu1,mu4,mu5,mu8)*d_(mu2,mu7)*d_(mu3,mu6)*I
       - 4*epsM(mu1,mu4,mu6,mu7)*d_(mu2,mu3)*d_(mu5,mu8)*I
       + 4*epsM(mu1,mu4,mu6,mu7)*d_(mu2,mu5)*d_(mu3,mu8)*I
       - 4*epsM(mu1,mu4,mu6,mu7)*d_(mu2,mu8)*d_(mu3,mu5)*I
       + 4*epsM(mu1,mu4,mu6,mu8)*d_(mu2,mu3)*d_(mu5,mu7)*I
       - 4*epsM(mu1,mu4,mu6,mu8)*d_(mu2,mu5)*d_(mu3,mu7)*I
       + 4*epsM(mu1,mu4,mu6,mu8)*d_(mu2,mu7)*d_(mu3,mu5)*I
       - 4*epsM(mu1,mu4,mu7,mu8)*d_(mu2,mu3)*d_(mu5,mu6)*I
       + 4*epsM(mu1,mu4,mu7,mu8)*d_(mu2,mu5)*d_(mu3,mu6)*I
       - 4*epsM(mu1,mu4,mu7,mu8)*d_(mu2,mu6)*d_(mu3,mu5)*I
       + 4*epsM(mu1,mu5,mu6,mu7)*d_(mu2,mu3)*d_(mu4,mu8)*I
       - 4*epsM(mu1,mu5,mu6,mu7)*d_(mu2,mu4)*d_(mu3,mu8)*I
       + 4*epsM(mu1,mu5,mu6,mu7)*d_(mu2,mu8)*d_(mu3,mu4)*I
       - 4*epsM(mu1,mu5,mu6,mu8)*d_(mu2,mu3)*d_(mu4,mu7)*I
       + 4*epsM(mu1,mu5,mu6,mu8)*d_(mu2,mu4)*d_(mu3,mu7)*I
       - 4*epsM(mu1,mu5,mu6,mu8)*d_(mu2,mu7)*d_(mu3,mu4)*I
       + 4*epsM(mu1,mu5,mu7,mu8)*d_(mu2,mu3)*d_(mu4,mu6)*I
       - 4*epsM(mu1,mu5,mu7,mu8)*d_(mu2,mu4)*d_(mu3,mu6)*I
       + 4*epsM(mu1,mu5,mu7,mu8)*d_(mu2,mu6)*d_(mu3,mu4)*I
       - 4*epsM(mu1,mu6,mu7,mu8)*d_(mu2,mu3)*d_(mu4,mu5)*I
       + 4*epsM(mu1,mu6,mu7,mu8)*d_(mu2,mu4)*d_(mu3,mu5)*I
       - 4*epsM(mu1,mu6,mu7,mu8)*d_(mu2,mu5)*d_(mu3,mu4)*I
       - 4*epsM(mu2,mu3,mu4,mu5)*d_(mu1,mu6)*d_(mu7,mu8)*I
       + 4*epsM(mu2,mu3,mu4,mu5)*d_(mu1,mu7)*d_(mu6,mu8)*I
       - 4*epsM(mu2,mu3,mu4,mu5)*d_(mu1,mu8)*d_(mu6,mu7)*I
       + 4*epsM(mu2,mu3,mu4,mu6)*d_(mu1,mu5)*d_(mu7,mu8)*I
       - 4*epsM(mu2,mu3,mu4,mu6)*d_(mu1,mu7)*d_(mu5,mu8)*I
       + 4*epsM(mu2,mu3,mu4,mu6)*d_(mu1,mu8)*d_(mu5,mu7)*I
       - 4*epsM(mu2,mu3,mu4,mu7)*d_(mu1,mu5)*d_(mu6,mu8)*I
       + 4*epsM(mu2,mu3,mu4,mu7)*d_(mu1,mu6)*d_(mu5,mu8)*I
       - 4*epsM(mu2,mu3,mu4,mu7)*d_(mu1,mu8)*d_(mu5,mu6)*I
       + 4*epsM(mu2,mu3,mu4,mu8)*d_(mu1,mu5)*d_(mu6,mu7)*I
       - 4*epsM(mu2,mu3,mu4,mu8)*d_(mu1,mu6)*d_(mu5,mu7)*I
       + 4*epsM(mu2,mu3,mu4,mu8)*d_(mu1,mu7)*d_(mu5,mu6)*I
       - 4*epsM(mu2,mu3,mu5,mu6)*d_(mu1,mu4)*d_(mu7,mu8)*I
       + 4*epsM(mu2,mu3,mu5,mu6)*d_(mu1,mu7)*d_(mu4,mu8)*I
       - 4*epsM(mu2,mu3,mu5,mu6)*d_(mu1,mu8)*d_(mu4,mu7)*I
       + 4*epsM(mu2,mu3,mu5,mu7)*d_(mu1,mu4)*d_(mu6,mu8)*I
       - 4*epsM(mu2,mu3,mu5,mu7)*d_(mu1,mu6)*d_(mu4,mu8)*I
       + 4*epsM(mu2,mu3,mu5,mu7)*d_(mu1,mu8)*d_(mu4,mu6)*I
       - 4*epsM(mu2,mu3,mu5,mu8)*d_(mu1,mu4)*d_(mu6,mu7)*I
       + 4*epsM(mu2,mu3,mu5,mu8)*d_(mu1,mu6)*d_(mu4,mu7)*I
       - 4*epsM(mu2,mu3,mu5,mu8)*d_(mu1,mu7)*d_(mu4,mu6)*I
       - 4*epsM(mu2,mu3,mu6,mu7)*d_(mu1,mu4)*d_(mu5,mu8)*I
       + 4*epsM(mu2,mu3,mu6,mu7)*d_(mu1,mu5)*d_(mu4,mu8)*I
       - 4*epsM(mu2,mu3,mu6,mu7)*d_(mu1,mu8)*d_(mu4,mu5)*I
       + 4*epsM(mu2,mu3,mu6,mu8)*d_(mu1,mu4)*d_(mu5,mu7)*I
       - 4*epsM(mu2,mu3,mu6,mu8)*d_(mu1,mu5)*d_(mu4,mu7)*I
       + 4*epsM(mu2,mu3,mu6,mu8)*d_(mu1,mu7)*d_(mu4,mu5)*I
       - 4*epsM(mu2,mu3,mu7,mu8)*d_(mu1,mu4)*d_(mu5,mu6)*I
       + 4*epsM(mu2,mu3,mu7,mu8)*d_(mu1,mu5)*d_(mu4,mu6)*I
       - 4*epsM(mu2,mu3,mu7,mu8)*d_(mu1,mu6)*d_(mu4,mu5)*I
       + 4*epsM(mu2,mu4,mu5,mu6)*d_(mu1,mu3)*d_(mu7,mu8)*I
       - 4*epsM(mu2,mu4,mu5,mu6)*d_(mu1,mu7)*d_(mu3,mu8)*I
       + 4*epsM(mu2,mu4,mu5,mu6)*d_(mu1,mu8)*d_(mu3,mu7)*I
       - 4*epsM(mu2,mu4,mu5,mu7)*d_(mu1,mu3)*d_(mu6,mu8)*I
       + 4*epsM(mu2,mu4,mu5,mu7)*d_(mu1,mu6)*d_(mu3,mu8)*I
       - 4*epsM(mu2,mu4,mu5,mu7)*d_(mu1,mu8)*d_(mu3,mu6)*I
       + 4*epsM(mu2,mu4,mu5,mu8)*d_(mu1,mu3)*d_(mu6,mu7)*I
       - 4*epsM(mu2,mu4,mu5,mu8)*d_(mu1,mu6)*d_(mu3,mu7)*I
       + 4*epsM(mu2,mu4,mu5,mu8)*d_(mu1,mu7)*d_(mu3,mu6)*I
       + 4*epsM(mu2,mu4,mu6,mu7)*d_(mu1,mu3)*d_(mu5,mu8)*I
       - 4*epsM(mu2,mu4,mu6,mu7)*d_(mu1,mu5)*d_(mu3,mu8)*I
       + 4*epsM(mu2,mu4,mu6,mu7)*d_(mu1,mu8)*d_(mu3,mu5)*I
       - 4*epsM(mu2,mu4,mu6,mu8)*d_(mu1,mu3)*d_(mu5,mu7)*I
       + 4*epsM(mu2,mu4,mu6,mu8)*d_(mu1,mu5)*d_(mu3,mu7)*I
       - 4*epsM(mu2,mu4,mu6,mu8)*d_(mu1,mu7)*d_(mu3,mu5)*I
       + 4*epsM(mu2,mu4,mu7,mu8)*d_(mu1,mu3)*d_(mu5,mu6)*I
       - 4*epsM(mu2,mu4,mu7,mu8)*d_(mu1,mu5)*d_(mu3,mu6)*I
       + 4*epsM(mu2,mu4,mu7,mu8)*d_(mu1,mu6)*d_(mu3,mu5)*I
       - 4*epsM(mu2,mu5,mu6,mu7)*d_(mu1,mu3)*d_(mu4,mu8)*I
       + 4*epsM(mu2,mu5,mu6,mu7)*d_(mu1,mu4)*d_(mu3,mu8)*I
       - 4*epsM(mu2,mu5,mu6,mu7)*d_(mu1,mu8)*d_(mu3,mu4)*I
       + 4*epsM(mu2,mu5,mu6,mu8)*d_(mu1,mu3)*d_(mu4,mu7)*I
       - 4*epsM(mu2,mu5,mu6,mu8)*d_(mu1,mu4)*d_(mu3,mu7)*I
       + 4*epsM(mu2,mu5,mu6,mu8)*d_(mu1,mu7)*d_(mu3,mu4)*I
       - 4*epsM(mu2,mu5,mu7,mu8)*d_(mu1,mu3)*d_(mu4,mu6)*I
       + 4*epsM(mu2,mu5,mu7,mu8)*d_(mu1,mu4)*d_(mu3,mu6)*I
       - 4*epsM(mu2,mu5,mu7,mu8)*d_(mu1,mu6)*d_(mu3,mu4)*I
       + 4*epsM(mu2,mu6,mu7,mu8)*d_(mu1,mu3)*d_(mu4,mu5)*I
       - 4*epsM(mu2,mu6,mu7,mu8)*d_(mu1,mu4)*d_(mu3,mu5)*I
       + 4*epsM(mu2,mu6,mu7,mu8)*d_(mu1,mu5)*d_(mu3,mu4)*I
       - 4*epsM(mu3,mu4,mu5,mu6)*d_(mu1,mu2)*d_(mu7,mu8)*I
       + 4*epsM(mu3,mu4,mu5,mu6)*d_(mu1,mu7)*d_(mu2,mu8)*I
       - 4*epsM(mu3,mu4,mu5,mu6)*d_(mu1,mu8)*d_(mu2,mu7)*I
       + 4*epsM(mu3,mu4,mu5,mu7)*d_(mu1,mu2)*d_(mu6,mu8)*I
       - 4*epsM(mu3,mu4,mu5,mu7)*d_(mu1,mu6)*d_(mu2,mu8)*I
       + 4*epsM(mu3,mu4,mu5,mu7)*d_(mu1,mu8)*d_(mu2,mu6)*I
       - 4*epsM(mu3,mu4,mu5,mu8)*d_(mu1,mu2)*d_(mu6,mu7)*I
       + 4*epsM(mu3,mu4,mu5,mu8)*d_(mu1,mu6)*d_(mu2,mu7)*I
       - 4*epsM(mu3,mu4,mu5,mu8)*d_(mu1,mu7)*d_(mu2,mu6)*I
       - 4*epsM(mu3,mu4,mu6,mu7)*d_(mu1,mu2)*d_(mu5,mu8)*I
       + 4*epsM(mu3,mu4,mu6,mu7)*d_(mu1,mu5)*d_(mu2,mu8)*I
       - 4*epsM(mu3,mu4,mu6,mu7)*d_(mu1,mu8)*d_(mu2,mu5)*I
       + 4*epsM(mu3,mu4,mu6,mu8)*d_(mu1,mu2)*d_(mu5,mu7)*I
       - 4*epsM(mu3,mu4,mu6,mu8)*d_(mu1,mu5)*d_(mu2,mu7)*I
       + 4*epsM(mu3,mu4,mu6,mu8)*d_(mu1,mu7)*d_(mu2,mu5)*I
       - 4*epsM(mu3,mu4,mu7,mu8)*d_(mu1,mu2)*d_(mu5,mu6)*I
       + 4*epsM(mu3,mu4,mu7,mu8)*d_(mu1,mu5)*d_(mu2,mu6)*I
       - 4*epsM(mu3,mu4,mu7,mu8)*d_(mu1,mu6)*d_(mu2,mu5)*I
       + 4*epsM(mu3,mu5,mu6,mu7)*d_(mu1,mu2)*d_(mu4,mu8)*I
       - 4*epsM(mu3,mu5,mu6,mu7)*d_(mu1,mu4)*d_(mu2,mu8)*I
       + 4*epsM(mu3,mu5,mu6,mu7)*d_(mu1,mu8)*d_(mu2,mu4)*I
       - 4*epsM(mu3,mu5,mu6,mu8)*d_(mu1,mu2)*d_(mu4,mu7)*I
       + 4*epsM(mu3,mu5,mu6,mu8)*d_(mu1,mu4)*d_(mu2,mu7)*I
       - 4*epsM(mu3,mu5,mu6,mu8)*d_(mu1,mu7)*d_(mu2,mu4)*I
       + 4*epsM(mu3,mu5,mu7,mu8)*d_(mu1,mu2)*d_(mu4,mu6)*I
       - 4*epsM(mu3,mu5,mu7,mu8)*d_(mu1,mu4)*d_(mu2,mu6)*I
       + 4*epsM(mu3,mu5,mu7,mu8)*d_(mu1,mu6)*d_(mu2,mu4)*I
       - 4*epsM(mu3,mu6,mu7,mu8)*d_(mu1,mu2)*d_(mu4,mu5)*I
       + 4*epsM(mu3,mu6,mu7,mu8)*d_(mu1,mu4)*d_(mu2,mu5)*I
       - 4*epsM(mu3,mu6,mu7,mu8)*d_(mu1,mu5)*d_(mu2,mu4)*I
       - 4*epsM(mu4,mu5,mu6,mu7)*d_(mu1,mu2)*d_(mu3,mu8)*I
       + 4*epsM(mu4,mu5,mu6,mu7)*d_(mu1,mu3)*d_(mu2,mu8)*I
       - 4*epsM(mu4,mu5,mu6,mu7)*d_(mu1,mu8)*d_(mu2,mu3)*I
       + 4*epsM(mu4,mu5,mu6,mu8)*d_(mu1,mu2)*d_(mu3,mu7)*I
       - 4*epsM(mu4,mu5,mu6,mu8)*d_(mu1,mu3)*d_(mu2,mu7)*I
       + 4*epsM(mu4,mu5,mu6,mu8)*d_(mu1,mu7)*d_(mu2,mu3)*I
       - 4*epsM(mu4,mu5,mu7,mu8)*d_(mu1,mu2)*d_(mu3,mu6)*I
       + 4*epsM(mu4,mu5,mu7,mu8)*d_(mu1,mu3)*d_(mu2,mu6)*I
       - 4*epsM(mu4,mu5,mu7,mu8)*d_(mu1,mu6)*d_(mu2,mu3)*I
       + 4*epsM(mu4,mu6,mu7,mu8)*d_(mu1,mu2)*d_(mu3,mu5)*I
       - 4*epsM(mu4,mu6,mu7,mu8)*d_(mu1,mu3)*d_(mu2,mu5)*I
       + 4*epsM(mu4,mu6,mu7,mu8)*d_(mu1,mu5)*d_(mu2,mu3)*I
       - 4*epsM(mu5,mu6,mu7,mu8)*d_(mu1,mu2)*d_(mu3,mu4)*I
       + 4*epsM(mu5,mu6,mu7,mu8)*d_(mu1,mu3)*d_(mu2,mu4)*I
       - 4*epsM(mu5,mu6,mu7,mu8)*d_(mu1,mu4)*d_(mu2,mu3)*I
      ;


*: for the cases with even more gamma's than 8, we need to resort to the direct computation by FORM 
*: using the standard 4-d definition of gamma5 below. 
id gam(FIVE,?mu) = -I/24 * epsM(mus1,mus2,mus3,mus4) * gam(mus1,mus2,mus3,mus4,?mu);



.sort

* ------------> Error message If there is still any g5 in a closed loop<------------
id gam(y1?,?a1,FIVE,?a2,y1?)=ALARM(y1,?a1,FIVE,?a2,y1);

.sort


* Now we let form do the traces without gamma5
repeat;
id gam(y1?,?a,y1?)=g_(1,?a);
endrepeat;

tracen,1;

*>>>>>>>>
*: we now release the coefficients of the traces / strings of gamma matrices
id bracket1([MM.s2]?) = [MM.s2];
.sort
*<<<<<<<<



* first we define eps(mu1,mu2,mu3,mu4) as epsM
* we need that because we have defined epsM as antisymmetric
id eps(mu1?,mu2?,mu3?,mu4?)=epsM(mu1,mu2,mu3,mu4);
.sort

* This is true when the NP model is an eft
#if `isnoteft'==0
*** Start change from JSP
*** We are going to implement the 4D property of gamma matrices
*** gam(mu1,mu2,mu3)=d_(mu1,mu2)*gam(mu3)+d_(mu2,mu3)*gam(mu1)
***                 -d_(mu1,mu3)*gam(mu2)
***                 +I*epsM(mu1,mu2,mu3,mu4)*gam(mu4,five)
*** This is only valid in 4D therefore only for the RGEMaker mode
**** The above sign is correct for eps^{0123}=+1 (peskin), the warsaw paper uses the opposite convention
*** note that we write gam(five,mu4) so we change the sign

repeat;
* JSP *
id, once gam(y1?,?a,mu1?,mu2?,mu3?,?b,y2?)=d_(mu1,mu2)*gam(y1,?a,mu3,?b,y2)+d_(mu2,mu3)*gam(y1,?a,mu1,?b,y2)-d_(mu1,mu3)*gam(y1,?a,mu2,?b,y2)-I*epsM(mu1,mu2,mu3,mu79)*gam(y1,?a,FIVE,mu79,?b,y2);
*id, once gam(y1?,?a,mu1?,mu2?,mu3?,?b,y2?)=d_(mu1,mu2)*gam(y1,?a,mu3,?b,y2)+d_(mu2,mu3)*gam(y1,?a,mu1,?b,y2)-d_(mu1,mu3)*gam(y1,?a,mu2,?b,y2)+I*e_(mu1,mu2,mu3,mu79)*gam(y1,?a,FIVE,mu79,?b,y2);
sum mu79;
** Anticommute gamma5 and use gamma5^2=1 to take it to the left
repeat;
id,once gam(y1? , ?a, FIVE, FIVE, ?b) =gam(y1,?a,?b);
id,once gam(y1?, ?a, mu1?, FIVE, ?b) =-gam(y1,?a,FIVE, mu1, ?b);
endrepeat;

endrepeat;

.sort

* Now replace them with our own dummy indices
* we use mul replace to replace variables inside functions
#do jc=50,90;
    mul replace_(N1_?, mu'jc');
    .sort
#enddo;

.sort

******************+
*** We now introduce ga(mu1,mu2)*eps(mu1,mu2,mu3,mu4)=-I*gam(FIVE,mu3,mu4)+I*gam(FIVE,mu4,mu3)
*** this is for our convention for the eps, the warsaw basis people had the opposite sign
** Put the two gammas that are contracted with e_ together
repeat id,once gam(y1?,?a,mu1?,mu?,?c,mu2?,?b,y2?)*epsM(mu1?,mu2?,mu3?,mu4?)=-gam(y1,?a,mu,mu1,?c,mu2,?b,y2)*epsM(mu1,mu2,mu3,mu4)+2*gam(y1,?a,?c,mu2,?b,y2)*epsM(mu,mu2,mu3,mu4);
*repeat id,once gam(y1?,?a,mu1?,mu?,?c,mu2?,?b,y2?)*epsM(mu1?,mu2?,mu3?,mu4?)=-gam(y1,?a,mu,mu1,?c,mu2,?b,y2)*epsM(mu1,mu2,mu3,mu4)+2*d_(mu1,mu)*gam(y1,?a,?c,mu2,?b,y2)*epsM(mu1,mu2,mu3,mu4);
** implement the property above
repeat id,once gam(y1?,?a,mu1?,mu2?,?b,y2?)*epsM(mu1?,mu2?,mu3?,mu4?)=-(I*gam(y1,?a,FIVE,mu3,mu4,?b,y2)-I*gam(y1,?a,FIVE,mu4,mu3,?b,y2));
*repeat id,once gam(y1?,?a,mu1?,mu2?,?b,y2?)*epsM(mu1?,mu2?,mu3?,mu4?)=I*gam(y1,?a,FIVE,mu3,mu4,?b,y2)-I*gam(y1,?a,FIVE,mu4,mu3,?b,y2);
*** WE introduced new FIVEs, put them all to the left and use FIVE*FIVE=1
repeat;
id,once gam(y1? , ?a, FIVE, FIVE, ?b) =gam(y1,?a,?b);
id,once gam(y1?, ?a, mu1?, FIVE, ?b) =-gam(y1,?a,FIVE, mu1, ?b);
endrepeat;
*****************+

* We now go from epsM (minkowskian) to I e_ with e_ euclidean

**** This was at the end before (make sure it does not screw anythin up!!!)
* JSP *
id epsM(mu1?,mu2?,mu3?,mu4?) = I*e_(mu1,mu2,mu3,mu4);
*id eps(mu1?,mu2?,mu3?,mu4?) = e_(mu1,mu2,mu3,mu4);
.sort

repeat contract;
.sort

**** The contraction might reintroduce repeated indices inside a single gamma chain, eliminate them again (in 4D)
repeat;
id gam(y1?, ?a, mua?, mua?, ?b, y2?)= 4*gam(y1, ?a, ?b, y2);
id,once gam(y1?, ?a, mua?, mu1?, ?b, mua?, ?c, y2?) =  - gam(y1, ?a, mu1, mua, ?b, mua, ?c, y2)+2*gam(y1, ?a, ?b, mu1, ?c, y2);
endrepeat;


*** End change from JSP


#endif


************************************
************************************
* END of Gamma
************************************
************************************


#endprocedure


#procedure partialfractioning(isnoteft,looporder)

************************************

id k1.k1 = invprop(k1, 0);
id prop(k1, 0)*invprop(k1, 0)=1;

repeat;
id,once prop(k1, [MM.s1]?)*prop(k1, [MM.s2]?!{[MM.s1]?})= DEN([MM.s1],[MM.s2])*(prop(k1, [MM.s1])- prop(k1, [MM.s2]));
endrepeat;


id DEN(0,[MM.s1]?)=-1/[MM.s1]^2;
id DEN([MM.s1]?,0)=1/[MM.s1]^2;


* Deal with left over powers of k1.k1 in the numerator
repeat;
id invprop(k1,0)*prop(k1,[MM.s1]?)=1+[MM.s1]^2*prop(k1,[MM.s1]);
endrepeat;

* Keep the UV divergent term for massless loops only 1/k^4 is relevant
* This has to be done only if the theory is an EFT
* We do this only at one loop
*#if `isnoteft'==0
#if ((`isnoteft'==0) && (`looporder'==1))
id only prop(k1, 0)^2=I/FourPi^2/[MM.epsi];
* everything else is 0
multiply [MM.epsi];
id [MM.epsi]=0;
multiply 1/[MM.epsi];
#endif
*-----  zero of dimreg.
id prop(k1, 0)=0;
id invprop(k1, 0)=0;

.sort


#endprocedure

#procedure IBP()

*---- IBP identity
#do jc=0,8
id,once prop(k1,[MM.s1]?)^(10-'jc') =
prop(k1, [MM.s1])^(9-'jc')/[MM.s1]^2*(D/2-(9-'jc'))/(9-'jc');
#enddo;
#endprocedure

#procedure momentumconservation(n)

* Let's impose momentum conservation
* first we rename the polarizations to avoid imposing momentum
* consevation on them

#do iii=1,`n'
id Evect(p'iii',mu1?)=pol'iii'(mu1);
#enddo

if (`n'>1);
mul replace_(p1,-p2-...-p`n');
endif;

#call linearize



* We now let form know about momenta explicitly
* So that it will write the result in a compact universal form
id Mom(k1?,mu1?)=k1(mu1);
id dotp(k1?,p1?)=k1.p1;
* We first do epsM and the all other eps's
id epsM(mu1?,mu2?,mu3?,mu4?) = I*e_(mu1,mu2,mu3,mu4);
id eps(?a) = e_(?a);
.sort
#endprocedure


#procedure standardorderinggammas()
* standard ordering for gammas
id gam(y1?,?mu,y2?) = SPI(y1)*GAM(?mu)*SPI(y2);
chainout GAM;
repeat;
disorder GAM(mu2?)*GAM(mu1?) = -GAM(mu1)*GAM(mu2) +2* d_(mu1,mu2)*GAM();
id GAM()*GAM(mu?)=GAM(mu);
endrepeat;
*repeat disorder GAM(mu2?)*GAM(mu1?) = -GAM(mu1)*GAM(mu2) +2* d_(mu1,mu2)*GAM();
id GAM(mu?)*GAM(mu?) = D*GAM();
id GAM(p1?)*GAM(p1?) = p1.p1*GAM();
chainin GAM;
id SPI(y1?)*GAM(?mu)*SPI(y2?) = gam(y1,?mu,y2);
.sort
#endprocedure

#procedure epsexpansion(isnoteft,looporder)
**** we can now expand in eps
**** Note that in RGEMaker mode (isnoteft==0) we have already kept only the 1/[MM.epsi] terms.
id D =4-2*[MM.epsi];
repeat;
id [MM.epsi]^2=0;
id den([MM.s1]?, [MM.s2]?)=1/[MM.s1]+[MM.s2]/[MM.s1]*[MM.epsi]*den([MM.s1], [MM.s2]);
endrepeat;
** Now we have expanded all powers of D except for massive propagators, keeping the finite and order eps term.
** The result now is of the following form
** In RGEMaker mode    result=1/eps *( a + b eps)
** In MM mode result=(1+prop(k1,M))*(a+b eps)
** We are not interested in the finite term in RGEMaker mode so we set it to zero (at one loop order)
#if ((`isnoteft'==0) && (`looporder'==1))
multiply [MM.epsi];
id [MM.epsi]=0;
multiply 1/[MM.epsi];
#endif
** the 1 in MM mode is proportional to a scaleless integral that we have to set to 0
#if ((`isnoteft'!=0) && (`looporder'==1))
** There is no invepsilonbar in the current expression
** we multiply everything by invepsilonbar
multiply invepsilonbar;
** we now divide by invepsilonbar the terms proportional to a heavy prop
id prop(k1,[MM.s1]?)=1/invepsilonbar*prop(k1,[MM.s1]);
** and set to 0 invepsilonbar (and with it all the terms not proportional to a heavy prop)
id invepsilonbar=0;
#endif
id prop(k1,[MM.s1]?)=I*[MM.s1]^2/FourPi^2*(1+1/[MM.epsi]-Log([MM.s1]^2));

** CAREFULL !!! Pablo trying
**#if (`isnoteft'!=1)
#if (`looporder'==1)
id [MM.epsi]=0;
#endif


id 1/[MM.epsi]=invepsilonbar;
id [MM.epsi]=1/invepsilonbar;
#endprocedure

#procedure dummylorentz()
* dummy lorentz indices
** Internally sum over repeated indices
* we have two types of e_, one with gauge indices and one with lorentz indices
* we only want to sum over the one with four (hopefully lorentz) indices
id e_(mu1?,mu2?,mu3?,mu4?)=e_(mu1,mu2,mu3,mu4)*ind(mu1,mu2,mu3,mu4);
* get indices externally
id gam(?i)=gam(?i)*ind(?i);
* split ind into product of ind with one variable
chainout ind;
* if they are repeated keep only one, otherwise remove it
id ind(mu?)*ind(mu?) = ind(mu);
also ind(mu?)=1;
also ind(FIVE?)=1;
b ind;
.sort;
* Now if there are leftover ind (they were repeated)
* let FORM turn them into dummy variables
repeat;
if (count(ind,1)>0);
  once ind(mu?$sum) = 1;
  sum $sum;
endif;
endrepeat;
.sort
* Now replace them with our own dummy indices
* we use mul replace to replace variables inside functions
#do jc=1,30;
    mul replace_(N1_?, mu'jc');
    .sort
#enddo;

#endprocedure

#procedure dummyindices(tsett,name)
  id F?!flmassFunc(?i)=F(?i)*ind(?i);
  chainout ind;
  repeat;
    id, once ind(F?!flmassFunc(?i))=ind(?i);
  endrepeat;
  id ind(mu?!`tsett')=1;
* The line below removes ind(funct(i))
  id ind(FIVE?)=1;
  id ind(mu?)*ind(mu?)=ind(mu);
  also ind(?i)=1;
  b ind;
  .sort
  repeat;
  if (count(ind,1)>0);
    once ind(mu?$sum) = 1;
    sum $sum;
  endif;
  endrepeat;
 .sort
* Now replace them with our own dummy indices
* we use mul replace to replace variables inside functions
* this works because non-dummy indices (external ones) are
* close to 100
  #do jc=1,30;
    mul replace_(N1_?, `name'`jc');
    .sort
  #enddo;

#endprocedure

#procedure finalize()
* First we simplify ratios of functions

repeat;
#do nnn=1,10;
id, once ind?(mu1?)/ind?(mu1?)^(11-'nnn')=1/ind(mu1)^(10-'nnn');
#enddo
endrepeat;
.sort

* deltas with repeated indices are different depending on whether the index
* appears also outside the delta or not
* we start with the case in which the delta is contracted with an extra index
* this one does the DEN(M(i),M(j)) and the case of positive powers of functions
* with indices (positive powers of mass or an extra coupling)

id deltaFF(mu1?,mu1?)*ind?(?a,val?(mu1?),?b)=ind(?a,val(mu1),?b);

* we now do the case in which we have functions raised to negative powers,
* like M(i)^-2, or to positive powers inside functions, like Log(M(i)^2).

#do nnn=1,20;
id deltaFF(mu1?,mu1?)*ind?(?a,val?(mu1?)^'nnn',?b)=ind(?a,val(mu1)^'nnn',?b);
id deltaFF(mu1?,mu1?)/ind?(mu1?)^'nnn'=1/ind(mu1)^'nnn';
#enddo;

* finally, if we have any deltaFF(mu1?,mu1?) remaining it is not
* contracted with any futher index and it should be equal to the
* dimension of the index

id deltaFF(mu1?,mu1?)=d_(mu1,mu1);

#endprocedure

#procedure collectflavor()

id F?flFunc(?i) = G(F(?i));
repeat id G([MM.s1]?) * G([MM.s2]?) = G([MM.s1]*[MM.s2]);
argToExtraSymbol G;
id G([MM.s1]?) = [MM.s1];
.sort

#endprocedure

#procedure collectgauge()
b `gFunc';
.sort
collect G, G;
makeinteger G;
toPolynomial onlyfunctions G;
.sort
#endprocedure

#procedure doall(n,setlightmasses,isnoteft,looporder)
#call preparedeltas
#call prepare
#call expandmomenta(setlightmasses,`n')
#call tensorreduction
#call newjoingammas
#call flipgammas
#call dogammas(`n',`isnoteft')
#call partialfractioning(`isnoteft',`looporder')
#call IBP
#call momentumconservation(`n')
#call identifydeltas
#call standardorderinggammas
#call epsexpansion(`isnoteft',`looporder')
#call dummylorentz()
id ubspin(?a)=1;
id uspin(?a)=1;
id vbspin(?a)=1;
id vspin(?a)=1;
id ubspin1(?a)=1;
id uspin1(?a)=1;
id vbspin1(?a)=1;
id vspin1(?a)=1;
#call calldummyindices
#call finalize()
id I^2=-1;
.sort
#endprocedure

#procedure collectterms()
#call collectflavor
#call collectgauge
#endprocedure
