{ stdenv, fetchurl }:

stdenv.mkDerivation rec {
  name = "libasyncns-0.8";

  src = fetchurl {
    url = "http://0pointer.de/lennart/projects/libasyncns/${name}.tar.gz";
    sha256 = "0x5b6lcic4cd7q0bx00x93kvpyzl7n2abbgvqbrlzrfb8vknc6jg";
  };

  configureFlags = stdenv.lib.optionals (stdenv.hostPlatform != stdenv.buildPlatform) [
    "ac_cv_func_malloc_0_nonnull=yes"
    "ac_cv_func_realloc_0_nonnull=yes"
  ];

  meta = with stdenv.lib; {
    homepage = "http://0pointer.de/lennart/projects/libasyncns/";
    description = "A C library for Linux/Unix for executing name service queries asynchronously";
    license = licenses.lgpl21;
    platforms = platforms.unix;
  };
}