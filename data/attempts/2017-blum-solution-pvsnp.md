---
id: blum-2017
claims: [not-equal]
year: 2017
authors: Norbert Blum
title: "A Solution of the P versus NP problem"
status: retracted
---

In August 2017, Norbert Blum (Bonn) — a respected complexity theorist and
holder of the long-standing record for general circuit lower bounds —
published a claimed proof that P is not equal to NP, by extending the
Razborov–Berg–Ulfberg approximation method from monotone to general
(non-monotone) circuits and deriving an exponential lower bound for CLIQUE.
The paper *A Solution of the P versus NP problem*
is available at [arXiv:1708.03486](https://arxiv.org/abs/1708.03486).

This was the most closely watched attempt of the decade: Scott Aaronson,
Luca Trevisan, Dick Lipton & Ken Regan, and John Baez all wrote analyses
within days, and Aaronson publicly declined to renew his famous bet on it.
Within roughly one week the proof was refuted: the same technique would
apply to the [Tardos function](https://en.wikipedia.org/wiki/Tardos_function),
a monotone function computable in polynomial time, yielding a contradiction.
The error was pinpointed in Theorem 6 of the paper
(a [discussion on CS Theory StackExchange](https://cstheory.stackexchange.com/questions/38836/norbert-blums-claimed-proof-that-p-does-not-equal-np)
collects the analysis).

To his great credit, Blum promptly confirmed the flaw: the revised arXiv
version states "the proof is wrong", and he published a detailed account of
his mistake. The episode is considered a textbook example of both why such
proofs fail (relativizing and natural-proofs style barriers) and of honest
scientific conduct under scrutiny.

Further reading:

- Scott Aaronson:
  [In which it is strongly hinted that Norbert Blum has proved P ≠ NP… and in which it turns out he hasn't](https://scottaaronson.blog/?p=3409)
- Luca Trevisan:
  [On Norbert Blum's claimed proof that P does not equal NP](https://lucatrevisan.wordpress.com/2017/08/15/on-norbert-blums-claimed-proof-that-p-does-not-equal-np/)
- Dick Lipton & Ken Regan:
  [On the edge of eclipses and P=NP](https://rjlipton.com/2017/08/17/on-the-edge-of-eclipses-and-pnp/)
