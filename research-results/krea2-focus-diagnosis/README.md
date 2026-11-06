# Krea2 reference-focus diagnosis

These five first-pass outputs use the same beach-club reference, seed
`27012026`, 10-step LCM/simple sampling at CFG 1, 1280x1600 canvas, and an
explicit ordinary iPhone Photo-mode prompt with Portrait mode off.

1. `01-inspired-full-stack.png`: General Edit, FameGrid, Realism Engine, and
   KNP with Inspired/beside placement.
2. `02-inspired-general-edit-knp.png`: FameGrid and Realism Engine bypassed.
3. `03-inspired-general-edit-only.png`: FameGrid, Realism Engine, and KNP
   bypassed.
4. `04-balanced-50-full-stack.png`: full stack with 50% spatial overlap.
5. `05-feathered-75-full-stack.png`: full stack with seamless 75% spatial
   overlap.

The Inspired outputs retain portrait-like background focus falloff even after
all style LoRAs are bypassed. Balanced 50% recovers some environmental detail.
Feathered 75% best inherits the reference's resolved phone-photo background
without the hard quarter-width seam. This isolates reference-coordinate overlap
as the controlling variable; prompt wording and the optional Alex identity
finish are not the source of the blur.
