import base64
import os
import zlib
from typing import Set, Union


def get_md5(data: Union[str, bytes]) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    import hashlib
    m = hashlib.md5()
    m.update(data)
    s = m.hexdigest()
    return s


def _check_md5(vname: str, data: Union[str, bytes], length: int, md5: str, orig_filename: str) -> None:
    if len(data) != length:
        msg = (
            f"Mismatch for variable {vname!r}."
            f"The length does not match: expected {length}, got {len(data)}."
        )
        raise ValueError(msg)

    computed = get_md5(data)
    if computed != md5:
        msg = f"Mismatch for variable {vname!r}. The file was corrupted. Please re-pack."
        raise ValueError(msg)
    fn = os.path.join(os.path.dirname(__file__), orig_filename)
    if os.path.exists(fn):
        orig_data: Union[bytes, str]
        if isinstance(data, str):
            with open(fn, "r") as f1:
                orig_data = f1.read()
        else:
            with open(fn, "rb") as f2:
                orig_data = f2.read()

        if orig_data != data:
            msg = f"Packed data {fn} changed. Please repack."
            try:
                from . import logger 
            except ImportError:
                pass
            else:
                logger.error(msg)

            # if False:
            # fns = f"pack-orig-{vname}", f"pack-curr-{vname}"
            #     try:
            #         with open(fns[0], "wb") as fw1:
            #             fw1.write(as_bytes(orig_data))
            #         with open(fns[1], "wb") as fw2:
            #             fw2.write(as_bytes(data))
            #     except:
            #         logger.error("Could not write diff files.", e=traceback.format_exc())
    else:
        # logger.warning(f"Original file {fn!r} does not exist.")
        pass

warned: Set[str] = set()

def get_updated_str(data: str, orig_filename: str) -> str:
    fn = os.path.join(os.path.dirname(__file__), orig_filename)
    if os.path.exists(fn):
        with open(fn, "r") as f1:
            orig_data = f1.read()
            return orig_data
    else:
        if orig_filename not in warned:
            warned.add(orig_filename)
            try:
                from . import logger # type: ignore
            except ImportError:
                pass
            else:
                logger.warning(f"Original file {fn!r} does not exist; cannot get updated data.")
        
        return data


def get_updated_bytes(data: bytes, orig_filename: str) -> bytes:
    fn = os.path.join(os.path.dirname(__file__), orig_filename)
    if os.path.exists(fn):
        with open(fn, "rb") as f1:
            orig_data = f1.read()
            return orig_data
    else:
        return data


def as_bytes(x: Union[str, bytes]) -> bytes:
    if isinstance(x, str):
        return x.encode()
    return x


def decode_to_bytes(b: bytes) -> bytes:
    decoded = base64.b64decode(b)
    return zlib.decompress(decoded)


def decode_to_str(b: bytes) -> str:
    decoded = base64.b64decode(b)
    return zlib.decompress(decoded).decode()


__all__ = [
    "lib1_parts_discrete_posets_mcdpr1_yaml",
    "lib1_parts_discrete_posets_mcdpr1_yaml_fresh",
    "lib1_parts_e01_empty_models_mcdpr1_yaml",
    "lib1_parts_e01_empty_models_mcdpr1_yaml_fresh",
    "lib1_parts_e02_direct_connection_models_mcdpr1_yaml",
    "lib1_parts_e02_direct_connection_models_mcdpr1_yaml_fresh",
    "lib1_parts_e03_splitter1_models_mcdpr1_yaml",
    "lib1_parts_e03_splitter1_models_mcdpr1_yaml_fresh",
    "lib1_parts_e04_splitter2_models_mcdpr1_yaml",
    "lib1_parts_e04_splitter2_models_mcdpr1_yaml_fresh",
    "lib1_parts_e05_multf_models_mcdpr1_yaml",
    "lib1_parts_e05_multf_models_mcdpr1_yaml_fresh",
    "lib1_parts_e05_multr_models_mcdpr1_yaml",
    "lib1_parts_e05_multr_models_mcdpr1_yaml_fresh",
    "lib1_parts_e05_scalef_models_mcdpr1_yaml",
    "lib1_parts_e05_scalef_models_mcdpr1_yaml_fresh",
    "lib1_parts_e05_scaler_models_mcdpr1_yaml",
    "lib1_parts_e05_scaler_models_mcdpr1_yaml_fresh",
    "lib1_parts_e05_sumf_models_mcdpr1_yaml",
    "lib1_parts_e05_sumf_models_mcdpr1_yaml_fresh",
    "lib1_parts_e06_addf_models_mcdpr1_yaml",
    "lib1_parts_e06_addf_models_mcdpr1_yaml_fresh",
    "lib1_parts_e06_addr_models_mcdpr1_yaml",
    "lib1_parts_e06_addr_models_mcdpr1_yaml_fresh",
    "lib1_parts_e06_sumr_models_mcdpr1_yaml",
    "lib1_parts_e06_sumr_models_mcdpr1_yaml_fresh",
    "lib1_parts_e07_ceil_models_mcdpr1_yaml",
    "lib1_parts_e07_ceil_models_mcdpr1_yaml_fresh",
    "lib1_parts_e07_floor_models_mcdpr1_yaml",
    "lib1_parts_e07_floor_models_mcdpr1_yaml_fresh",
    "lib1_parts_e10_conversions1_models_mcdpr1_yaml",
    "lib1_parts_e10_conversions1_models_mcdpr1_yaml_fresh",
    "lib1_parts_e10_conversions2_models_mcdpr1_yaml",
    "lib1_parts_e10_conversions2_models_mcdpr1_yaml_fresh",
    "lib1_parts_nats_posets_mcdpr1_yaml",
    "lib1_parts_nats_posets_mcdpr1_yaml_fresh",
    "lib1_parts_reals_posets_mcdpr1_yaml",
    "lib1_parts_reals_posets_mcdpr1_yaml_fresh",
    "lib1_parts_reals_with_units_posets_mcdpr1_yaml",
    "lib1_parts_reals_with_units_posets_mcdpr1_yaml_fresh",
    "resources",
]


lib1_parts_discrete_posets_mcdpr1_yaml: str = decode_to_str(
    b"eJxNijkKwDAMBHu/QkXafEAPSJ0v+FiwiA+I9X8i202Kgd1hjhEzqmdHpKIFTJc0Udx9QE0+0hLTfiio"
    b"aDrYnZSNaAQjGd6Ae1G8Sm8rmZJoJzOeO60dfns38efhPkb+JHg=",
)


def lib1_parts_discrete_posets_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_discrete_posets_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.discrete.posets.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_discrete_posets_mcdpr1_yaml",
    lib1_parts_discrete_posets_mcdpr1_yaml,
    149,
    "da99ccdf93e76923fea64b4e4e3d047b",
    "../../assets/test-data/downloaded/lib1-parts.discrete.posets.mcdpr1.yaml",
)
lib1_parts_e01_empty_models_mcdpr1_yaml: str = decode_to_str(
    b"eJw1yjEOgCAMheGdU3TwFKw6G3fjQKDGRmgNlMl4d4nB7X15/1D8gclZA6CkES2Mki4ppDi7hGFa2nMS"
    b"Bwu/98peSdhFUsJi4X5MxiI1+y6W0JcXZvzq5nUzL1bHJqc=",
)


def lib1_parts_e01_empty_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e01_empty_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e01_empty.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e01_empty_models_mcdpr1_yaml",
    lib1_parts_e01_empty_models_mcdpr1_yaml,
    111,
    "5eded1fa7fca3ac02260dc9224ff0e72",
    "../../assets/test-data/downloaded/lib1-parts.e01_empty.models.mcdpr1.yaml",
)
lib1_parts_e02_direct_connection_models_mcdpr1_yaml: str = decode_to_str(
    b"eJy9kDsOwjAMhvecwkOlTkjMWWFhqXqFPhxh0dhV4gwIcXeStBWcgAxW/Pvx2W7idEc/WAOgpAtauIhf"
    b"JZJiN3icr32OPIhnC4fvEk9KwsNCShhLqSsGoPk2K28r6yWi7sqO6JIfMcQqjqIq3kJ7bquvslq4sSMm"
    b"fVYl5V/MCa0JGCWFaWOG/zBZ5syD19tMwox188w/gQu5RU3+PcjTgiu3lC10TGwhmA+kLGsW",
)


def lib1_parts_e02_direct_connection_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e02_direct_connection_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e02_direct_connection.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e02_direct_connection_models_mcdpr1_yaml",
    lib1_parts_e02_direct_connection_models_mcdpr1_yaml,
    363,
    "b6057c5b1d569ea09dfeb12e782cfacd",
    "../../assets/test-data/downloaded/lib1-parts.e02_direct_connection.models.mcdpr1.yaml",
)
lib1_parts_e03_splitter1_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzNVT1uwyAU3nOKN0TyFCnJyJqoUodGUTt0RMQGldaAxU+ljM3U3qNDz5WTFIgd27HdIUNcBgse8P3w"
    b"8GNq0hcqCJoAWG5zimClRKEMt3RDBM3WWz/zxmWGoBozJ1PLlSQ5t5yasJWFD8C0BgvttG2rDLVlpKTY"
    b"OLGj2sTgTlmrBIJknsSxVQWCe8m45HYfI873jF+QTDQ1yun0xKnx4jasgWp5GyqpspM5/Kq4xEz6I+93"
    b"WRI9cVHk9FmToiWpTp3PTTddoeEzVAe739qAvT6L/TYvT9WfazOfURTD8/FlRR2L8XVkRUXZUVAyPVBq"
    b"N2tH8jLXDWmaC5/vd9qY8Xcr1bwIlwEBg+PXt0/B8fABx8+f0DmUK+/Gtw6w+g8iiJQV6+P1emJ4q1Xm"
    b"0nrWuJ2pEWZ9oEOwg0b7rQ6Z7dodX0eqpKSxXPnDmQHTHiQuDJURtcriOYyrMoJi/QgvmUKt+oLCY3Ed"
    b"3GIAbtmCa9bYvf+3Gpv+YrrYhsnkF0yw/ws=",
)


def lib1_parts_e03_splitter1_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e03_splitter1_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e03_splitter1.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e03_splitter1_models_mcdpr1_yaml",
    lib1_parts_e03_splitter1_models_mcdpr1_yaml,
    1927,
    "ac5e9a2f4da020e29c7ff2a8c893dc6e",
    "../../assets/test-data/downloaded/lib1-parts.e03_splitter1.models.mcdpr1.yaml",
)
lib1_parts_e04_splitter2_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzNVb1uwyAQ3vMUN0TKFCnJyJqqUjtEUTt0tIiNVdrAWYArZWym9j069Ln8JAWMazu2M2SIw2K4M98P"
    b"h46pjl+ZoGQCYLjZMwJrFBlqbtiGCpbcbW3mncuEQLVOcxkbjpLuueFMu61ptHQfgGkN50a5cYuamRAJ"
    b"JJtc7JjSPrhDY1AQmC1mfm0wI/AgUy65OfhIbmfa/jDzVKvrUCmmMVdxaVBdh1NiUvJFb8hllEp75P0n"
    b"G4ieucj27EXRrCWpLp09sG653IhUtKjmHfR+cwMG+0z2Gz2tZdCxHF9Hq9heFh1fVJJVlB0FgenR3pJN"
    b"qHNDluLC1vqDNTL2XsWKZ+4iEEiL4ycUX79ucoTi+wdU+HE9vmuAp1sQQaWsWO8v1+PDW4VJHtdZne90"
    b"jTDvAx2CHTTab3XIbNfu+DpilJL5TmUPZw6psiCdBnYg7q1xjxWWSdcxSatd/oejk42u450HXl0MvGwB"
    b"n9tbdRqbpw26Oqwmf11ZAcc=",
)


def lib1_parts_e04_splitter2_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e04_splitter2_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e04_splitter2.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e04_splitter2_models_mcdpr1_yaml",
    lib1_parts_e04_splitter2_models_mcdpr1_yaml,
    1932,
    "8bb893879ecd7ec400103d18ca2c516f",
    "../../assets/test-data/downloaded/lib1-parts.e04_splitter2.models.mcdpr1.yaml",
)
lib1_parts_e05_multf_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzFVb1uwyAQ3vMUDJE8RUoysraq1CFRlA4dEcFYRbUB8VPJYyN1qPoafbI8SQHj2olxh6iKWYA7833f"
    b"3eFjrskLrTCcAWCYKSkEd6KSQjNDt7ii+f3OeV4ZzyFo94XlxDDBcckMo9ofLdDKTwDMOzg/moM7oamJ"
    b"lkiytdWBKh2MB2GMqCDIllnYGyEheOQF48zUwWLdSrsPskC1vg2VolpYRZoA1W04ucgbPiSVyNM5jRRP"
    b"rJIlfVZYnonpiuZSNSyUH0jIZbseoKfDGgktFV46xMsqRh2r6XWclTnIUt16Olm5bCkHCiLTBu2pRhtb"
    b"GibLeoN5jWLdeyIVq1zt32jP424YUUz6iwFBcTq+n74+3HQEp89voOJn++kzAICQWmJC/1/KYkCdEoQ5"
    b"b5kertcQzDv3N1vSebU99O7YIgU6BjsaXDrTY7keZnt6HURwTkPHcslZgEI5kEEjq6F/bfxzJRqn75kw"
    b"NsxfA7o44nve35DrKyBXZ5DpU21/gaGx9Eg6h5r9AAVyAVQ=",
)


def lib1_parts_e05_multf_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e05_multf_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e05_multf.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e05_multf_models_mcdpr1_yaml",
    lib1_parts_e05_multf_models_mcdpr1_yaml,
    1918,
    "cf9998520ab5d047b14a6f529f66a15e",
    "../../assets/test-data/downloaded/lib1-parts.e05_multf.models.mcdpr1.yaml",
)
lib1_parts_e05_multr_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzFVb1qwzAQ3vMUGgKeAklGrS2BDgmhHToaR5apqPWDfgIeG+hQ+hp9sjxJT7JdO7G8hBJrsK2T7vu+"
    b"u5NPc0PeKM/wDCHLbEkxepBcScMs3WWc5o97WHlnIseonRdOEMukyEpmGTXetfAPhOYdmB+1214aahtL"
    b"Q7Fz/EC1CcaDtFZyjJJlEuZWKoyeRMEEs1WwOPgysCGZaWqk06Tm1OnqPqyean0fKiHzOriUiSN3pY2H"
    b"2LC8MK5K+qozdaGnqxsUZlgrP1LIJKC30wFBPLiRAGNBxgO9zitktl/RoEwqs5xeVy1kNb2QXLWUAwUN"
    b"0zbdOJFuoZxMldU2E1XaFL8nUjMOB+BIeytw0ohmyp8OjAp0/vpB+nz6OH9/wuvUbNtMnwGEoBIqI/T/"
    b"pSwG1DFBmRAt0/PtGoJ5r2XuSLdq3MF0CIsY6BjsaHDxTI/lepjt6XUQKQQNbQuSs0CFBpCw0bdH3PXG"
    b"P1vathFc9w9/mUl80WCwvy9uAVuNgK0vwPp9toLfqec0ynPl0/Tk2S+4TwcT",
)


def lib1_parts_e05_multr_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e05_multr_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e05_multr.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e05_multr_models_mcdpr1_yaml",
    lib1_parts_e05_multr_models_mcdpr1_yaml,
    1930,
    "15ea7bc6c0929b1c749e6a4ac925223f",
    "../../assets/test-data/downloaded/lib1-parts.e05_multr.models.mcdpr1.yaml",
)
lib1_parts_e05_scalef_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzNVEtqwzAQ3fsUswhkFUi22qYEukgoKbRLo9gyFbU0Qp9ADtBF6TV6spykki3Xdqx0VZp6YaSRZt68"
    b"N/abmeKFCUoyAMttzQisUSg03LIdFay8e/Anr1yWBLp95WRhOUpac8uZCalVeAHM+mLhadMe0DAbIxFi"
    b"58SBadMED2gtCgLz5bzZW1QE7mXFJbenJuL8yvgL80wzg04XLab+G0yJZYuXC1fbVRI0QjxyoWr2rKka"
    b"NdPr6IWaaheeHNWyW0+qp2ldoZail6Y4phl2I3mbtnS/vl1bpeogJx1EpG2+Zybf+vlwVZ/WKI2l0uZR"
    b"80Gjmguv+5ENTvx0C81VGAqBCs4fb7Bawvn9E3S8s7m9BABH92MXEe+J1o5tNIpxP8cQ9sVWA1gVbgxL"
    b"JKpeY3eV34DhECuSvIhdUkRlFC3Y76u9mKib0nz/H8ZMpSRZgVKyxib837eAys+TTNzj5L/WYNrYHgWb"
    b"ItGjvgP5RUKwmVHBdFbnA6QxgAFIf6CzL9H2pU0=",
)


def lib1_parts_e05_scalef_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e05_scalef_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e05_scalef.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e05_scalef_models_mcdpr1_yaml",
    lib1_parts_e05_scalef_models_mcdpr1_yaml,
    1589,
    "3974b96a2701df7c01207fda12ee89fd",
    "../../assets/test-data/downloaded/lib1-parts.e05_scalef.models.mcdpr1.yaml",
)
lib1_parts_e05_scaler_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzNVMlOwzAQvecr5lCpp4r26mtRJQ5FFUhwjNzEERbxIi+R+gn8B1/GlzBOHOos7QlRfIjiZebNe7Ms"
    b"bPHGBCUZgOOuZgS2SmhluWOPVLDy/oA371yWBPp95WXhuJK05o4zG0yr8AFYnJ2F1ZkdlGUunkSIRy+O"
    b"zNj28KicU4LAcr1s905pAg+y4pK7U3vi8c/ig2VmmFXeFB2m+RtMqcoOL+eyEb52Da0928yCR6hnLnTN"
    b"Xg3Vg6DOeqJgUw3DypEhQvTbCcA8wwss55jOsx0yDruB0m1kStv17eMqdQ85iSAi7fOdl/keVeS6Pm2V"
    b"tI5Kl0fdk0ANF6h9w5IbzHRhuA6JIVDBHWzW8PXxCSa+2N1eAIDGX40i4r2EKt0ZJYbxtMWLzjYJrA4v"
    b"UhczXi+xu8gvYZhiRZKjszFFrDVNC/b7aq8m6s5p/vQf0kylJFmhpGTtoMBGXEGF+exCCVOJjEbSz0Xe"
    b"dy/p2jbMdkUGfU2wplN/6Tw6Ye0nJtehRoZxgGXflCyxVw==",
)


def lib1_parts_e05_scaler_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e05_scaler_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e05_scaler.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e05_scaler_models_mcdpr1_yaml",
    lib1_parts_e05_scaler_models_mcdpr1_yaml,
    1621,
    "bdf1242b955e22310d960c2e274e1001",
    "../../assets/test-data/downloaded/lib1-parts.e05_scaler.models.mcdpr1.yaml",
)
lib1_parts_e05_sumf_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzFVbtqwzAU3fMVdwhkKIEko7bSUuiQENKho1AkmYpaD/QoZGy2/ke/LF9SyY84ie1SQom9yLpXOg9d"
    b"cTV29I1LgkYAXvicI3jQ0mgnPF8RydnjOmbehWII6nkWFPVCK5ILL7hLWzM8TwPAuIFLX7lxrR33VaQi"
    b"WQW55dYVwa32XksEk9mkmHttEDyrTCjhd0UkxD8XF0wKqsVtqCx3OlhaGrS34VSalXzYBdl9pBXDi5Am"
    b"56+WmDMtTc3iSbXrlD7suZWzetbC7/bV463LX7fHyzIelcyHV3JW6UJYjITcD6+MmZqypaBiWuINd/ie"
    b"sSVRO1xV/kSfFTJW/4OfZOIVo1aYdDUQZIf9J9ylYQ+Hr2+w1TJtnCGU//8RTFuW/3ZZNsNXA4AoVbM+"
    b"Xa+nCK+tZoE2WRe2rkGYdoH2wfYa7bbaZ7Ztd3gdVCvFiy4WD2cKmY0grea2Q+kBSi+YLpOpjaKyhx7n"
    b"+GJH2QZ/x1xcgzk/w+zcVjccVHeaE54mZ0c/w+QF6Q==",
)


def lib1_parts_e05_sumf_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e05_sumf_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e05_sumf.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e05_sumf_models_mcdpr1_yaml",
    lib1_parts_e05_sumf_models_mcdpr1_yaml,
    1943,
    "4873dc1a1e537bcfb68623fb97dcafa4",
    "../../assets/test-data/downloaded/lib1-parts.e05_sumf.models.mcdpr1.yaml",
)
lib1_parts_e06_addf_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzdVkFOwzAQvPcVe0DqASE1PVpwQEWVOFAhkOAYpYkjLGKvZTuV+gT+wct4CXbi0KRxC0Utrcghstf2"
    b"zs6sd+Uznb5QnpABgGGmoAQmyCVqZugs4TS7ubcrr0xkBJp5XorUMBRJwQyj2h3N3Q/gbOXMffWxe9TU"
    b"eIuHmJV8TpWujHM0BjmB4WhYzQ1KArciZ4KZZWUp7UjbDcOBohpLldaY6m8wBWY1XiyLUkdBUA/xyLgs"
    b"6LNKZCeYlY5WqL527otRjppxz3uY1gZqIXphil2abtaRtwpLrcZ7DCvaMa5MNpi9EDzUXfxAdXydZRMU"
    b"2iTCxF7vVpCKcav5grZWbGZTxaRLCIEcziEaweUVKL9hevyUACzKrVF4vKekKOlUIe/Gs3DmNcWl29F2"
    b"EfC6id1Gfhuy60mu2dYpotQySen+1b7oqfszzR9O4NIDJEJUfSdFsbAu7SU9YPeJToBysP+Mj1+E3/ef"
    b"az5nVJjJV6Z2bz4fb+8HbTy7378UOUfxv6vyd0VpK1LQqpLsVb2A3PZd0iuwpc2qe1VhveTeEcQ/Ir4M"
    b"8doBV4kdh+FTTaGQqkL6IK2OsRUqCmEFD3cRxy3I1YoafAJWBrHh",
)


def lib1_parts_e06_addf_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e06_addf_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e06_addf.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e06_addf_models_mcdpr1_yaml",
    lib1_parts_e06_addf_models_mcdpr1_yaml,
    2635,
    "1152ad2764168d59ece4e256afdc33ff",
    "../../assets/test-data/downloaded/lib1-parts.e06_addf.models.mcdpr1.yaml",
)
lib1_parts_e06_addr_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzdVktqwzAQ3ecUswhkUQLJVruQEuiiIbTQLo1jy1TU0ghJNuQIvUdP1pNUUpRE/qRtStOGemGksWfe"
    b"e6OZQUOdPVGekgGAYaakBObIJWpm6DLlNL9e2S/PTOQEdvuiEplhKNKSGUa1cy3cC2B4COaerdsKNTXB"
    b"EiCWFV9Tpb1xjcYgJzCajPzeoCRwIwommNl4S2VX2v4wGiiqsVLZFlP9DqbAfIuXMFHLstIop73IAeee"
    b"cVnSR5XKBqNDMm22ugl0T6IO6070fm1H9DU0ToPIfqFNsW7XSLLnhXJyBl4n0srlDrLDICDdJotKJLM8"
    b"n6PQJhUmCfmOOCrGbc5rGn2xx5spJt2BECjg7eUVFFzBdBL+WFzAmQDU1Yc0AuBDWlZ0oZA3CdXO3IKV"
    b"7o84RE/UY/KOCjwiMYhs2doSUWqZZvTn0z3uZPdrOb/7+6oHSIXw0ydDUduItkrPNX4uos270+cypuLn"
    b"42fG14wKM9+f0zdnzxnHzsnFlyHnKP53R54+i31L2n4U1PeRLc8xFHbobrm4CwOJbwt7a7IrbuKbzV25"
    b"kDSqntjjj2PFrbqxFRK5BJhoLBxwWm4erIdir2/E0S67gH262njO8R1F+Lk0",
)


def lib1_parts_e06_addr_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e06_addr_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e06_addr.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e06_addr_models_mcdpr1_yaml",
    lib1_parts_e06_addr_models_mcdpr1_yaml,
    2645,
    "d610426b8f462b4f8dca16c3365bb9d4",
    "../../assets/test-data/downloaded/lib1-parts.e06_addr.models.mcdpr1.yaml",
)
lib1_parts_e06_sumr_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzFVb1uwjAQ3nmKG5AYKiRg9Fa1QuoAQu3QMQqOo1pNbMs/SIxl63v0yXiSnoPTBOJIpaqIhyQ+++77"
    b"vjvnPDb0jZUpGQFYbgtG4EGWShpu2TotWfa4wZV3LjIC9Tx3glouRVpwy5nxrrl/AIybYH6c3DbSMBss"
    b"AWLtyi3TpjJupbWyJDCZTaq5lYrAk8i54HZfWRx+GdwwGWlmpNP0hKnntwFFpMVtkITMTtISLnaqcCau"
    b"MKC88FIV7FWn6oxPUzUsS7dSfiSYR1fYetoBiIvrERgTGRd6mVZMbLueFbPZ8KSQxXx4FpmqITsMAtIq"
    b"WTqR3GfZKhX7JFS8xU/zEqu+Y60VPF5Uc+WPBIEcjp9foI+HD7jzr0PYthxePIBURqWU/T+VaQf6d4RS"
    b"IWrs57+zqswbLTNHm1XjtqaJMI0F7QvbKzee+z6xXbnD86BSCFZ1L0zOFHKNQaqNvkuSpkX+2JK6m+Di"
    b"zF9nkpw1GYI3xtWB5vFAi7NA7Ta7xx+r5dOLceETWvLoG1PEAF4=",
)


def lib1_parts_e06_sumr_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e06_sumr_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e06_sumr.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e06_sumr_models_mcdpr1_yaml",
    lib1_parts_e06_sumr_models_mcdpr1_yaml,
    1929,
    "5425908ff226be82e1a967dfe67eb7cb",
    "../../assets/test-data/downloaded/lib1-parts.e06_sumr.models.mcdpr1.yaml",
)
lib1_parts_e07_ceil_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzNVMFOwzAMvfcrfJhUOCBt11yHkDgwTUVox6pLXRHRxFGSIu0T+A++jC8hSVvarkWcgOVQJXbs92zn"
    b"dWX5M8qCJQBOuBoZbElqssLhrpBY3u6950WokkF/rhrFnSBV1MIJtCG0Ch+A1ZAsrDZsTxZdZ+kgdo08"
    b"orHReCTnSDJI12k8O9IM7lUllHCnaGn8zvoLaWLQUmN4i2l+E9M69KZ0k54xUFS26HnW1Jih3aKo893h"
    b"abPIpsN+FFLXeDCFnrAcGuw7OG9qWDnpdb+fZV+u95ual+pern1acThN+h5pmWH/l7SmY5kTLXVPYsap"
    b"w37I48S6ro+oGiF9519x5PGj5kboMBYG3IddVdfw8fYOprty9/+jASBtdcHxEqhkl/gmAAqlWMJJKYwS"
    b"8y/3Birjs8+Ud2JQhT8hta6gdjaX+pcvP4sNap3k/jFBrywWJTWCHhwm+QSbpICx",
)


def lib1_parts_e07_ceil_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e07_ceil_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e07_ceil.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e07_ceil_models_mcdpr1_yaml",
    lib1_parts_e07_ceil_models_mcdpr1_yaml,
    1442,
    "33792070ecc13388d7f7bfcc0eac761c",
    "../../assets/test-data/downloaded/lib1-parts.e07_ceil.models.mcdpr1.yaml",
)
lib1_parts_e07_floor_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzNVMFugzAMvfMVPlRiO0xqr7luqrTDUNVq6hFRMFo0EkdJmNRP2H/sy/YlS0IYMJh2mtocELax3/Nz"
    b"zMqULygKlgBYbhtkcE9CkeEWs0Jg9bBzkVcuKwa9XbeytJxk0XDL0fjU2j8AVkMxf7q0HRm00RMhslac"
    b"UJvgPJG1JBik6zTYlhSDR1lzye05eIxF50o3Xbx1fuPMNNFoqNVlx0D/J4MBU1LV4eX7tsFtK7cNkc6z"
    b"4/NmkUCEO3ChGjzqQk2IDQo7Ceeq+pPr4X1WfbnFX9pcanW53bnoUxG8NRE/ECW1vgTRKa1K9ZAzBhHp"
    b"KQ8jc6PLo/IjcpoLp/4bjiJu3qXmyo+GQQ2f7x9Q+wI3+jZ+s73G+QCQMqoo8fIzAdhfA4lCSpaUJCWG"
    b"PXMX9w5q7WqFuF9strDV38G8v/EsXHX/vyQ2WQUGelJyvNFnd3dGKX+j/Uj26MkXagaEcA==",
)


def lib1_parts_e07_floor_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e07_floor_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e07_floor.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e07_floor_models_mcdpr1_yaml",
    lib1_parts_e07_floor_models_mcdpr1_yaml,
    1450,
    "97d1f3d49214444c3916f83a84c0ee42",
    "../../assets/test-data/downloaded/lib1-parts.e07_floor.models.mcdpr1.yaml",
)
lib1_parts_e10_conversions1_models_mcdpr1_yaml: str = decode_to_str(
    b"eJzFVMFqwzAMvecrdCgUBmXp1deOwi6lbIwdi+sozLS2jO0U+gn7j33ZvmS24zTLko0dxupDsCVLT3rK"
    b"88yJF1ScFQBe+iMyWJEy5KTHDVdY3W2D5yB1xaA7140WXpLmR+kluhhaxw/ArE8WVxu2JYc+WzLEplF7"
    b"tC4Z9+Q9KQbzcp7OngyDe11LLf05WZqwcwxUYdFRY0ULaf8B8qAKTVWLtxOkTyFDaHw5CZ2BHqUyR3y2"
    b"3AxK6skMbI0JjGtHpuz2o+zTzX3T4FST040O+I2HAcepKtvvr1DVoS2rMh3kqIKM9BTury4junhzdVaq"
    b"wPUJ8wRSSnTCShMHwaCGG1jD8nZZliW8v76BzffWV58IwMP1+Qcg4wwX+PelLEbQvyKl5sKTZXlm2ci1"
    b"ZkUQqsYksPDjLqC2AWWku3OYeXzzqHVFmbOBxi/m3ZewKNNB2p9iOzmxpKNPgL3DFh/QgH7i",
)


def lib1_parts_e10_conversions1_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e10_conversions1_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e10_conversions1.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e10_conversions1_models_mcdpr1_yaml",
    lib1_parts_e10_conversions1_models_mcdpr1_yaml,
    1410,
    "8ef6750a72b874683fd332aa802f5a26",
    "../../assets/test-data/downloaded/lib1-parts.e10_conversions1.models.mcdpr1.yaml",
)
lib1_parts_e10_conversions2_models_mcdpr1_yaml: str = decode_to_str(
    b"eJztWd1q2zAUvs9T6KJQ6MiSNIx1ZrsoHYHBUkrLtkuj2MoqZv0gyRm5XGEXY6+xJ8uTTLKtWI6lZk2T"
    b"JoXpJrZknfOdo0+ffnIkk1tEYNQBQGGVoQhcMMKZxApdQoLS91e65RumaQTs+zSnicKMwgwrjKTpmmKp"
    b"IE2QeQbgqLZpStn7ikmkqprK02VOJkjIonLClGIkAsf94+JdMR6BD3SKKVbzoibXTzICpCOQZLlISs+S"
    b"I5Q+gdtpLjJGv8qeLDJFniLUWx2m7FCWlqHGmM5InqmB13Xl6AYTnqEvAvIGpHosAfCMnymxzqu2bl9b"
    b"DvzxBWL0xemPtZnjk9teaaAxyAU8xmV/v+BqAlhAgz0CKtlhKlJuvbZAVM7G8Sin8VgPL+bZfAzpPK7I"
    b"4OAUmGhCzJDTopmXCMwNW3QGwOLXHyAWdz8Wv3/qn7vqs9GBUAYAPSIcWhXaJp5uy78PFaTUerreHENR"
    b"fSVYmid1q8wnsrbQ9RkNmQ0G5093KOHhibBnPHYexATTXM5glqNnp5Dd/sv+YHjWPzsdbkkr9yyVS2z/"
    b"ok3XSMbnaXrBqNlFqI2k6QWoU2gBgLfvgNihSD1u1ACY5feCqtx/NoweCUaa8Aqim0HxYODmS9fUtqen"
    b"x2cVeaDtEOU6gOoR0r3l5axaT+KE0Zk2q5m+K2Hbr16QgIoJJA9u1q7XsxskdGov10pYypfRedfP5XHM"
    b"Dn47co8stoTxBIzA8M3wde/07NXgtG9KuY9bdoEE8rViYcV6DHk8jm8SmKH4E+dIuJ51fhudvJbCwnOP"
    b"9IT2BuHdwQq7yjKFiWIiWk2I80VLk3YVR1ujHhxNwtIDzHdTw0xx9sUl2+I0h9lGlPvIvj8DyrVTYIlX"
    b"c65nOPifeDua6E3KuS+jtbx7mmNLjfb6QBA1WXvfmnROJhhR9dilqbkMHcrArE7ehBHC6O7A+ebjAyHu"
    b"kkHe7dKDETpTMIMTlDlbny7oO8+DTqvDPu+X7CzdxaFg842oPhBQVGzkdR67YCrsKmjuiqP6onhZF9vN"
    b"dVTeo3aMo7JL3VJcpW9ibuA1Zy7Jfdaca5qAQRdeEIJ7lJlH9m6m4XDlE/snRdu6c8AKOzC4POF4+zrh"
    b"6Me2Q28OAhH9BZwYioE=",
)


def lib1_parts_e10_conversions2_models_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_e10_conversions2_models_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.e10_conversions2.models.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_e10_conversions2_models_mcdpr1_yaml",
    lib1_parts_e10_conversions2_models_mcdpr1_yaml,
    6550,
    "c82585c7a83af500a45a04c8042d5736",
    "../../assets/test-data/downloaded/lib1-parts.e10_conversions2.models.mcdpr1.yaml",
)
lib1_parts_nats_posets_mcdpr1_yaml: str = decode_to_str(
    b"eJwNx7ENgEAIAMCeKShMaLVlAxvjCr5iJPqPESzcXrq7ztdD6sKAeGrbGGdziVxoXMI4vbXI41Aswioj"
    b"9QRhN+PYdm0aH3hIlgaCN+9Jgh+sjBrN",
)


def lib1_parts_nats_posets_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_nats_posets_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.nats.posets.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_nats_posets_mcdpr1_yaml",
    lib1_parts_nats_posets_mcdpr1_yaml,
    86,
    "28d9b5c1929b628cc44a946a8b15b57a",
    "../../assets/test-data/downloaded/lib1-parts.nats.posets.mcdpr1.yaml",
)
lib1_parts_reals_posets_mcdpr1_yaml: str = decode_to_str(
    b"eJxTKU7OSM1NtOJSUMjOzEuxUgjIL04tAfJKMktyUq0U/Epzk1KLirmS8ktK8nOtFNQN1LlK8gusFDzz"
    b"0jLzMksquUqBZDFQQp0LAKsgGC4=",
)


def lib1_parts_reals_posets_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_reals_posets_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.reals.posets.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_reals_posets_mcdpr1_yaml",
    lib1_parts_reals_posets_mcdpr1_yaml,
    76,
    "d11a5177837a3e14e75754b3cfbe61b5",
    "../../assets/test-data/downloaded/lib1-parts.reals.posets.mcdpr1.yaml",
)
lib1_parts_reals_with_units_posets_mcdpr1_yaml: str = decode_to_str(
    b"eJxTKU7OSM1NtOJSUMjOzEuxUgjIL04tAfJKMktyUq0U/Epzk1KLirmS8ktK8nOtFNQN1LlK8gusFDzz"
    b"0jLzMksquUqBZLGVQnZ4BhcAxbQZCg==",
)


def lib1_parts_reals_with_units_posets_mcdpr1_yaml_fresh() -> str:
    return get_updated_str(
        lib1_parts_reals_with_units_posets_mcdpr1_yaml,
        "../../assets/test-data/downloaded/lib1-parts.reals_with_units.posets.mcdpr1.yaml",
    )


_check_md5(
    "lib1_parts_reals_with_units_posets_mcdpr1_yaml",
    lib1_parts_reals_with_units_posets_mcdpr1_yaml,
    77,
    "76c89aa9190ae359a5e49e3e5a9778b9",
    "../../assets/test-data/downloaded/lib1-parts.reals_with_units.posets.mcdpr1.yaml",
)

resources = {
    "lib1-parts.discrete.posets.mcdpr1.yaml": lib1_parts_discrete_posets_mcdpr1_yaml,
    "lib1-parts.e01_empty.models.mcdpr1.yaml": lib1_parts_e01_empty_models_mcdpr1_yaml,
    "lib1-parts.e02_direct_connection.models.mcdpr1.yaml": lib1_parts_e02_direct_connection_models_mcdpr1_yaml,
    "lib1-parts.e03_splitter1.models.mcdpr1.yaml": lib1_parts_e03_splitter1_models_mcdpr1_yaml,
    "lib1-parts.e04_splitter2.models.mcdpr1.yaml": lib1_parts_e04_splitter2_models_mcdpr1_yaml,
    "lib1-parts.e05_multf.models.mcdpr1.yaml": lib1_parts_e05_multf_models_mcdpr1_yaml,
    "lib1-parts.e05_multr.models.mcdpr1.yaml": lib1_parts_e05_multr_models_mcdpr1_yaml,
    "lib1-parts.e05_scalef.models.mcdpr1.yaml": lib1_parts_e05_scalef_models_mcdpr1_yaml,
    "lib1-parts.e05_scaler.models.mcdpr1.yaml": lib1_parts_e05_scaler_models_mcdpr1_yaml,
    "lib1-parts.e05_sumf.models.mcdpr1.yaml": lib1_parts_e05_sumf_models_mcdpr1_yaml,
    "lib1-parts.e06_addf.models.mcdpr1.yaml": lib1_parts_e06_addf_models_mcdpr1_yaml,
    "lib1-parts.e06_addr.models.mcdpr1.yaml": lib1_parts_e06_addr_models_mcdpr1_yaml,
    "lib1-parts.e06_sumr.models.mcdpr1.yaml": lib1_parts_e06_sumr_models_mcdpr1_yaml,
    "lib1-parts.e07_ceil.models.mcdpr1.yaml": lib1_parts_e07_ceil_models_mcdpr1_yaml,
    "lib1-parts.e07_floor.models.mcdpr1.yaml": lib1_parts_e07_floor_models_mcdpr1_yaml,
    "lib1-parts.e10_conversions1.models.mcdpr1.yaml": lib1_parts_e10_conversions1_models_mcdpr1_yaml,
    "lib1-parts.e10_conversions2.models.mcdpr1.yaml": lib1_parts_e10_conversions2_models_mcdpr1_yaml,
    "lib1-parts.nats.posets.mcdpr1.yaml": lib1_parts_nats_posets_mcdpr1_yaml,
    "lib1-parts.reals.posets.mcdpr1.yaml": lib1_parts_reals_posets_mcdpr1_yaml,
    "lib1-parts.reals_with_units.posets.mcdpr1.yaml": lib1_parts_reals_with_units_posets_mcdpr1_yaml,
}
