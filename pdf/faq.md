









**Keywords:** FAQ, Git, Tools, Setup


# Frequently asked questions


## I get asked for password when I access github

It's likely because the remote is set to https and not SSH

```
$git remote -v
origin https://github.com/analogicus/lelo_gr01_sky130a.git
```

then do 

```
git remote set-url origin git@github.com:analogicus/lelo_gr01_sky130a.git
```

Or it could be because you have not setup public/private key access to github. 

