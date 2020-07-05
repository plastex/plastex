### Source distributions of project development dependencies

{
  nixpkgsPath = builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/02c71d719d556a2caf3c4ccfeaff657e5550da0a.tar.gz";
    sha256 = "1bh9svzg2vz8rm9l02mj9v4y6xqsmrdn2jq2j55kp7sclbyrfclm";
  };
  
  nixPythonPath = builtins.fetchTarball {
    url = "https://github.com/nyraghu/nix-python/archive/1b8e506325176af190d6ffd167d83513a7dbf7c6.tar.gz";
    sha256 = "0amfd6nwy6jxhh70wgzcr142lf3nrjb1vjb9cw2gk53m4ni9vrm5";
  };
  
  nixNodeJsPath = builtins.fetchTarball {
    url = "https://github.com/nyraghu/nix-node-js/archive/a7555ffc461ac57f37d9d3db01d6da8399c6d04d.tar.gz";
    sha256 = "1n8l4nsn1lckwc2xvygg656a9i8fk69cznnmd5nag7y00zsy2dvn";
  };
}

### End of file
