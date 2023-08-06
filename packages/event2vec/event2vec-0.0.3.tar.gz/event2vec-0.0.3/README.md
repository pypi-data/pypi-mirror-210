# event2vec

**Documentation**: [https://straymat.gitlab.io/event2vec/](https://straymat.gitlab.io/event2vec/)

**Source Code**: [https://gitlab.com/strayMat/event2vec](https://gitlab.com/strayMat/event2vec)

## Overview

Electronic Health Record and claims contain sequences of care: every contact
between a patient and a healthcare system (either hospital, either insurance) is
recorded in a central database. Medical terminologies are often used to encode
the type of care : diagnoses, acts, drugs, laboratory, ...

Such healthcare trajectories can be viewed as sequence of tokens, similarly to
sequences of words.

This package propose to use matrix factorization as a simple and efficient way
to build event embedding from a medical observational database.
