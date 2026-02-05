footer: Carsten Wulff 2024
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2026-01-23

<!--pan_title: FAQ -->

# Frequently asked questions

---

## I get asked for password when I access github

It's likely because the remote is set to https and not SSH

```
$git remote -v
origin https://github.com/analogicus/lelo_gr01_sky130a.git
```

then do 

```
git remote set-url origin https://github.com/analogicus/lelo_gr01_sky130a.git
```

Or it could be because you have not setup public/private key access to github. 

---
