# coding: UTF-8
import sys
bstack1ll_opy_ = sys.version_info [0] == 2
bstack1l_opy_ = 2048
bstack1l1l_opy_ = 7
def bstack1ll1_opy_ (bstack1_opy_):
    global bstack111_opy_
    stringNr = ord (bstack1_opy_ [-1])
    bstack1l1_opy_ = bstack1_opy_ [:-1]
    bstack1lll_opy_ = stringNr % len (bstack1l1_opy_)
    bstack11l_opy_ = bstack1l1_opy_ [:bstack1lll_opy_] + bstack1l1_opy_ [bstack1lll_opy_:]
    if bstack1ll_opy_:
        bstack11_opy_ = unicode () .join ([unichr (ord (char) - bstack1l_opy_ - (bstackl_opy_ + stringNr) % bstack1l1l_opy_) for bstackl_opy_, char in enumerate (bstack11l_opy_)])
    else:
        bstack11_opy_ = str () .join ([chr (ord (char) - bstack1l_opy_ - (bstackl_opy_ + stringNr) % bstack1l1l_opy_) for bstackl_opy_, char in enumerate (bstack11l_opy_)])
    return eval (bstack11_opy_)
import atexit
import os
import signal
import sys
import yaml
import requests
import logging
import threading
import socket
import datetime
import string
import random
import json
import collections.abc
import re
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
bstack111l11l_opy_ = {
	bstack1ll1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧࠁ"): bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡻࡳࡦࡴࠪࠂ"),
  bstack1ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪࠃ"): bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡬ࡧࡼࠫࠄ"),
  bstack1ll1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬࠅ"): bstack1ll1_opy_ (u"ࠪࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠧࠆ"),
  bstack1ll1_opy_ (u"ࠫࡺࡹࡥࡘ࠵ࡆࠫࠇ"): bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡠࡹ࠶ࡧࠬࠈ"),
  bstack1ll1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫࠉ"): bstack1ll1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࠨࠊ"),
  bstack1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫࠋ"): bstack1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࠨࠌ"),
  bstack1ll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨࠍ"): bstack1ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩࠎ"),
  bstack1ll1_opy_ (u"ࠬࡪࡥࡣࡷࡪࠫࠏ"): bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡪࡥࡣࡷࡪࠫࠐ"),
  bstack1ll1_opy_ (u"ࠧࡤࡱࡱࡷࡴࡲࡥࡍࡱࡪࡷࠬࠑ"): bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡱࡷࡴࡲࡥࠨࠒ"),
  bstack1ll1_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡏࡳ࡬ࡹࠧࠓ"): bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡱࡩࡹࡽ࡯ࡳ࡭ࡏࡳ࡬ࡹࠧࠔ"),
  bstack1ll1_opy_ (u"ࠫࡦࡶࡰࡪࡷࡰࡐࡴ࡭ࡳࠨࠕ"): bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡶࡰࡪࡷࡰࡐࡴ࡭ࡳࠨࠖ"),
  bstack1ll1_opy_ (u"࠭ࡶࡪࡦࡨࡳࠬࠗ"): bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡶࡪࡦࡨࡳࠬ࠘"),
  bstack1ll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ࡏࡳ࡬ࡹࠧ࠙"): bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡏࡳ࡬ࡹࠧࠚ"),
  bstack1ll1_opy_ (u"ࠪࡸࡪࡲࡥ࡮ࡧࡷࡶࡾࡒ࡯ࡨࡵࠪࠛ"): bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡸࡪࡲࡥ࡮ࡧࡷࡶࡾࡒ࡯ࡨࡵࠪࠜ"),
  bstack1ll1_opy_ (u"ࠬ࡭ࡥࡰࡎࡲࡧࡦࡺࡩࡰࡰࠪࠝ"): bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡭ࡥࡰࡎࡲࡧࡦࡺࡩࡰࡰࠪࠞ"),
  bstack1ll1_opy_ (u"ࠧࡵ࡫ࡰࡩࡿࡵ࡮ࡦࠩࠟ"): bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡵ࡫ࡰࡩࡿࡵ࡮ࡦࠩࠠ"),
  bstack1ll1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫࠡ"): bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡩࡱ࡫࡮ࡪࡷࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬࠢ"),
  bstack1ll1_opy_ (u"ࠫࡲࡧࡳ࡬ࡅࡲࡱࡲࡧ࡮ࡥࡵࠪࠣ"): bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡲࡧࡳ࡬ࡅࡲࡱࡲࡧ࡮ࡥࡵࠪࠤ"),
  bstack1ll1_opy_ (u"࠭ࡩࡥ࡮ࡨࡘ࡮ࡳࡥࡰࡷࡷࠫࠥ"): bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡩࡥ࡮ࡨࡘ࡮ࡳࡥࡰࡷࡷࠫࠦ"),
  bstack1ll1_opy_ (u"ࠨ࡯ࡤࡷࡰࡈࡡࡴ࡫ࡦࡅࡺࡺࡨࠨࠧ"): bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯࡯ࡤࡷࡰࡈࡡࡴ࡫ࡦࡅࡺࡺࡨࠨࠨ"),
  bstack1ll1_opy_ (u"ࠪࡷࡪࡴࡤࡌࡧࡼࡷࠬࠩ"): bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡷࡪࡴࡤࡌࡧࡼࡷࠬࠪ"),
  bstack1ll1_opy_ (u"ࠬࡧࡵࡵࡱ࡚ࡥ࡮ࡺࠧࠫ"): bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡵࡵࡱ࡚ࡥ࡮ࡺࠧࠬ"),
  bstack1ll1_opy_ (u"ࠧࡩࡱࡶࡸࡸ࠭࠭"): bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡩࡱࡶࡸࡸ࠭࠮"),
  bstack1ll1_opy_ (u"ࠩࡥࡪࡨࡧࡣࡩࡧࠪ࠯"): bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡪࡨࡧࡣࡩࡧࠪ࠰"),
  bstack1ll1_opy_ (u"ࠫࡼࡹࡌࡰࡥࡤࡰࡘࡻࡰࡱࡱࡵࡸࠬ࠱"): bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡼࡹࡌࡰࡥࡤࡰࡘࡻࡰࡱࡱࡵࡸࠬ࠲"),
  bstack1ll1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡃࡰࡴࡶࡖࡪࡹࡴࡳ࡫ࡦࡸ࡮ࡵ࡮ࡴࠩ࠳"): bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡤࡪࡵࡤࡦࡱ࡫ࡃࡰࡴࡶࡖࡪࡹࡴࡳ࡫ࡦࡸ࡮ࡵ࡮ࡴࠩ࠴"),
  bstack1ll1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠬ࠵"): bstack1ll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࠩ࠶"),
  bstack1ll1_opy_ (u"ࠪࡶࡪࡧ࡬ࡎࡱࡥ࡭ࡱ࡫ࠧ࠷"): bstack1ll1_opy_ (u"ࠫࡷ࡫ࡡ࡭ࡡࡰࡳࡧ࡯࡬ࡦࠩ࠸"),
  bstack1ll1_opy_ (u"ࠬࡧࡰࡱ࡫ࡸࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬ࠹"): bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡰࡱ࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭࠺"),
  bstack1ll1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡎࡦࡶࡺࡳࡷࡱࠧ࠻"): bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡷࡶࡸࡴࡳࡎࡦࡶࡺࡳࡷࡱࠧ࠼"),
  bstack1ll1_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡓࡶࡴ࡬ࡩ࡭ࡧࠪ࠽"): bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡱࡩࡹࡽ࡯ࡳ࡭ࡓࡶࡴ࡬ࡩ࡭ࡧࠪ࠾"),
  bstack1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡍࡳࡹࡥࡤࡷࡵࡩࡈ࡫ࡲࡵࡵࠪ࠿"): bstack1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡘࡹ࡬ࡄࡧࡵࡸࡸ࠭ࡀ"),
  bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨࡁ"): bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨࡂ"),
  bstack1ll1_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨࡃ"): bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡲࡹࡷࡩࡥࠨࡄ"),
  bstack1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬࡅ"): bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬࡆ"),
  bstack1ll1_opy_ (u"ࠬ࡮࡯ࡴࡶࡑࡥࡲ࡫ࠧࡇ"): bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡮࡯ࡴࡶࡑࡥࡲ࡫ࠧࡈ"),
}
bstack11l11l_opy_ = [
  bstack1ll1_opy_ (u"ࠧࡰࡵࠪࡉ"),
  bstack1ll1_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫࡊ"),
  bstack1ll1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫࡋ"),
  bstack1ll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨࡌ"),
  bstack1ll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨࡍ"),
  bstack1ll1_opy_ (u"ࠬࡸࡥࡢ࡮ࡐࡳࡧ࡯࡬ࡦࠩࡎ"),
  bstack1ll1_opy_ (u"࠭ࡡࡱࡲ࡬ࡹࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ࡏ"),
]
bstack1l111l_opy_ = {
  bstack1ll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩࡐ"): [bstack1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡖࡕࡈࡖࡓࡇࡍࡆࠩࡑ"), bstack1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡗࡖࡉࡗࡥࡎࡂࡏࡈࠫࡒ")],
  bstack1ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ࡓ"): bstack1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅࡈࡉࡅࡔࡕࡢࡏࡊ࡟ࠧࡔ"),
  bstack1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨࡕ"): bstack1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡓࡇࡍࡆࠩࡖ"),
  bstack1ll1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬࡗ"): bstack1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡔࡒࡎࡊࡉࡔࡠࡐࡄࡑࡊ࠭ࡘ"),
  bstack1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵ࡙ࠫ"): bstack1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖ࡚ࠬ"),
  bstack1ll1_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰ࡛ࠫ"): bstack1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡇࡒࡂࡎࡏࡉࡑ࡙࡟ࡑࡇࡕࡣࡕࡒࡁࡕࡈࡒࡖࡒ࠭࡜"),
  bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ࡝"): bstack1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࠬ࡞"),
  bstack1ll1_opy_ (u"ࠨࡴࡨࡶࡺࡴࡔࡦࡵࡷࡷࠬ࡟"): bstack1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡔࡈࡖ࡚ࡔ࡟ࡕࡇࡖࡘࡘ࠭ࡠ"),
  bstack1ll1_opy_ (u"ࠪࡥࡵࡶࠧࡡ"): bstack1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅࡕࡖࠧࡢ"),
  bstack1ll1_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧࡣ"): bstack1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡕࡂࡔࡇࡕ࡚ࡆࡈࡉࡍࡋࡗ࡝ࡤࡊࡅࡃࡗࡊࠫࡤ"),
  bstack1ll1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫࡥ"): bstack1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫࡦ")
}
bstack11l11lll_opy_ = {
  bstack1ll1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫࡧ"): [bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡸࡷࡪࡸ࡟࡯ࡣࡰࡩࠬࡨ"), bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫ࡲࡏࡣࡰࡩࠬࡩ")],
  bstack1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨࡪ"): [bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷࡤࡱࡥࡺࠩ࡫"), bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ࡬")],
  bstack1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ࡭"): bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ࡮"),
  bstack1ll1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨ࡯"): bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨࡰ"),
  bstack1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࡱ"): bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࡲ"),
  bstack1ll1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧࡳ"): [bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡱࡲࡳࠫࡴ"), bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨࡵ")],
  bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧࡶ"): bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩࡷ"),
  bstack1ll1_opy_ (u"ࠬࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩࡸ"): bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩࡹ"),
  bstack1ll1_opy_ (u"ࠧࡢࡲࡳࠫࡺ"): bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡲࡳࠫࡻ"),
  bstack1ll1_opy_ (u"ࠩ࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫࡼ"): bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫࡽ"),
  bstack1ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨࡾ"): bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨࡿ")
}
bstack1l1ll1111_opy_ = {
  bstack1ll1_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩࢀ"): bstack1ll1_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫࢁ"),
  bstack1ll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࢂ"): [bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫࢃ"), bstack1ll1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ࢄ")],
  bstack1ll1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩࢅ"): bstack1ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪࢆ"),
  bstack1ll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪࢇ"): bstack1ll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧ࢈"),
  bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ࢉ"): [bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪࢊ"), bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡳࡧ࡭ࡦࠩࢋ")],
  bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬࢌ"): bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧࢍ"),
  bstack1ll1_opy_ (u"࠭ࡲࡦࡣ࡯ࡑࡴࡨࡩ࡭ࡧࠪࢎ"): bstack1ll1_opy_ (u"ࠧࡳࡧࡤࡰࡤࡳ࡯ࡣ࡫࡯ࡩࠬ࢏"),
  bstack1ll1_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ࢐"): [bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡳࡴ࡮ࡻ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ࢑"), bstack1ll1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫ࢒")],
  bstack1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡍࡳࡹࡥࡤࡷࡵࡩࡈ࡫ࡲࡵࡵࠪ࢓"): [bstack1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡘࡹ࡬ࡄࡧࡵࡸࡸ࠭࢔"), bstack1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹ࡙ࡳ࡭ࡅࡨࡶࡹ࠭࢕")]
}
bstack111ll_opy_ = [
  bstack1ll1_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡉ࡯ࡵࡨࡧࡺࡸࡥࡄࡧࡵࡸࡸ࠭࢖"),
  bstack1ll1_opy_ (u"ࠨࡲࡤ࡫ࡪࡒ࡯ࡢࡦࡖࡸࡷࡧࡴࡦࡩࡼࠫࢗ"),
  bstack1ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨ࢘"),
  bstack1ll1_opy_ (u"ࠪࡷࡪࡺࡗࡪࡰࡧࡳࡼࡘࡥࡤࡶ࢙ࠪ"),
  bstack1ll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡱࡸࡸࡸ࢚࠭"),
  bstack1ll1_opy_ (u"ࠬࡹࡴࡳ࡫ࡦࡸࡋ࡯࡬ࡦࡋࡱࡸࡪࡸࡡࡤࡶࡤࡦ࡮ࡲࡩࡵࡻ࢛ࠪ"),
  bstack1ll1_opy_ (u"࠭ࡵ࡯ࡪࡤࡲࡩࡲࡥࡥࡒࡵࡳࡲࡶࡴࡃࡧ࡫ࡥࡻ࡯࡯ࡳࠩ࢜"),
  bstack1ll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ࢝"),
  bstack1ll1_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭࢞"),
  bstack1ll1_opy_ (u"ࠩࡰࡷ࠿࡫ࡤࡨࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ࢟"),
  bstack1ll1_opy_ (u"ࠪࡷࡪࡀࡩࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩࢠ"),
  bstack1ll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬࢡ"),
]
bstack1llll_opy_ = [
  bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩࢢ"),
  bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪࢣ"),
  bstack1ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢤ"),
  bstack1ll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨࢥ"),
  bstack1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬࢦ"),
  bstack1ll1_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬࢧ"),
  bstack1ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧࢨ"),
  bstack1ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩࢩ"),
  bstack1ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩࢪ"),
]
bstack1lll1l1l_opy_ = [
  bstack1ll1_opy_ (u"ࠧࡶࡲ࡯ࡳࡦࡪࡍࡦࡦ࡬ࡥࠬࢫ"),
  bstack1ll1_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪࢬ"),
  bstack1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬࢭ"),
  bstack1ll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨࢮ"),
  bstack1ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡒࡵ࡭ࡴࡸࡩࡵࡻࠪࢯ"),
  bstack1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨࢰ"),
  bstack1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨ࡙ࡧࡧࠨࢱ"),
  bstack1ll1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬࢲ"),
  bstack1ll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࢳ"),
  bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧࢴ"),
  bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫࢵ"),
  bstack1ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࠪࢶ"),
  bstack1ll1_opy_ (u"ࠬࡵࡳࠨࢷ"),
  bstack1ll1_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩࢸ"),
  bstack1ll1_opy_ (u"ࠧࡩࡱࡶࡸࡸ࠭ࢹ"),
  bstack1ll1_opy_ (u"ࠨࡣࡸࡸࡴ࡝ࡡࡪࡶࠪࢺ"),
  bstack1ll1_opy_ (u"ࠩࡵࡩ࡬࡯࡯࡯ࠩࢻ"),
  bstack1ll1_opy_ (u"ࠪࡸ࡮ࡳࡥࡻࡱࡱࡩࠬࢼ"),
  bstack1ll1_opy_ (u"ࠫࡲࡧࡣࡩ࡫ࡱࡩࠬࢽ"),
  bstack1ll1_opy_ (u"ࠬࡸࡥࡴࡱ࡯ࡹࡹ࡯࡯࡯ࠩࢾ"),
  bstack1ll1_opy_ (u"࠭ࡩࡥ࡮ࡨࡘ࡮ࡳࡥࡰࡷࡷࠫࢿ"),
  bstack1ll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡏࡳ࡫ࡨࡲࡹࡧࡴࡪࡱࡱࠫࣀ"),
  bstack1ll1_opy_ (u"ࠨࡸ࡬ࡨࡪࡵࠧࣁ"),
  bstack1ll1_opy_ (u"ࠩࡱࡳࡕࡧࡧࡦࡎࡲࡥࡩ࡚ࡩ࡮ࡧࡲࡹࡹ࠭ࣂ"),
  bstack1ll1_opy_ (u"ࠪࡦ࡫ࡩࡡࡤࡪࡨࠫࣃ"),
  bstack1ll1_opy_ (u"ࠫࡩ࡫ࡢࡶࡩࠪࣄ"),
  bstack1ll1_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡘࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩࣅ"),
  bstack1ll1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲ࡙ࡥ࡯ࡦࡎࡩࡾࡹࠧࣆ"),
  bstack1ll1_opy_ (u"ࠧࡳࡧࡤࡰࡒࡵࡢࡪ࡮ࡨࠫࣇ"),
  bstack1ll1_opy_ (u"ࠨࡰࡲࡔ࡮ࡶࡥ࡭࡫ࡱࡩࠬࣈ"),
  bstack1ll1_opy_ (u"ࠩࡦ࡬ࡪࡩ࡫ࡖࡔࡏࠫࣉ"),
  bstack1ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ࣊"),
  bstack1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡇࡴࡵ࡫ࡪࡧࡶࠫ࣋"),
  bstack1ll1_opy_ (u"ࠬࡩࡡࡱࡶࡸࡶࡪࡉࡲࡢࡵ࡫ࠫ࣌"),
  bstack1ll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪ࣍"),
  bstack1ll1_opy_ (u"ࠧࡢࡲࡳ࡭ࡺࡳࡖࡦࡴࡶ࡭ࡴࡴࠧ࣎"),
  bstack1ll1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲ࡛࡫ࡲࡴ࡫ࡲࡲ࣏ࠬ"),
  bstack1ll1_opy_ (u"ࠩࡱࡳࡇࡲࡡ࡯࡭ࡓࡳࡱࡲࡩ࡯ࡩ࣐ࠪ"),
  bstack1ll1_opy_ (u"ࠪࡱࡦࡹ࡫ࡔࡧࡱࡨࡐ࡫ࡹࡴ࣑ࠩ"),
  bstack1ll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡐࡴ࡭ࡳࠨ࣒"),
  bstack1ll1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡎࡪ࣓ࠧ"),
  bstack1ll1_opy_ (u"࠭ࡤࡦࡦ࡬ࡧࡦࡺࡥࡥࡆࡨࡺ࡮ࡩࡥࠨࣔ"),
  bstack1ll1_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡐࡢࡴࡤࡱࡸ࠭ࣕ"),
  bstack1ll1_opy_ (u"ࠨࡲ࡫ࡳࡳ࡫ࡎࡶ࡯ࡥࡩࡷ࠭ࣖ"),
  bstack1ll1_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡏࡳ࡬ࡹࠧࣗ"),
  bstack1ll1_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡐࡴ࡭ࡳࡐࡲࡷ࡭ࡴࡴࡳࠨࣘ"),
  bstack1ll1_opy_ (u"ࠫࡨࡵ࡮ࡴࡱ࡯ࡩࡑࡵࡧࡴࠩࣙ"),
  bstack1ll1_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬࣚ"),
  bstack1ll1_opy_ (u"࠭ࡡࡱࡲ࡬ࡹࡲࡒ࡯ࡨࡵࠪࣛ"),
  bstack1ll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡂࡪࡱࡰࡩࡹࡸࡩࡤࠩࣜ"),
  bstack1ll1_opy_ (u"ࠨࡸ࡬ࡨࡪࡵࡖ࠳ࠩࣝ"),
  bstack1ll1_opy_ (u"ࠩࡰ࡭ࡩ࡙ࡥࡴࡵ࡬ࡳࡳࡏ࡮ࡴࡶࡤࡰࡱࡇࡰࡱࡵࠪࣞ"),
  bstack1ll1_opy_ (u"ࠪࡩࡸࡶࡲࡦࡵࡶࡳࡘ࡫ࡲࡷࡧࡵࠫࣟ"),
  bstack1ll1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲࡒ࡯ࡨࡵࠪ࣠"),
  bstack1ll1_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳࡃࡥࡲࠪ࣡"),
  bstack1ll1_opy_ (u"࠭ࡴࡦ࡮ࡨࡱࡪࡺࡲࡺࡎࡲ࡫ࡸ࠭࣢"),
  bstack1ll1_opy_ (u"ࠧࡴࡻࡱࡧ࡙࡯࡭ࡦ࡙࡬ࡸ࡭ࡔࡔࡑࣣࠩ"),
  bstack1ll1_opy_ (u"ࠨࡩࡨࡳࡑࡵࡣࡢࡶ࡬ࡳࡳ࠭ࣤ"),
  bstack1ll1_opy_ (u"ࠩࡪࡴࡸࡒ࡯ࡤࡣࡷ࡭ࡴࡴࠧࣥ"),
  bstack1ll1_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡔࡷࡵࡦࡪ࡮ࡨࣦࠫ"),
  bstack1ll1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡒࡪࡺࡷࡰࡴ࡮ࠫࣧ"),
  bstack1ll1_opy_ (u"ࠬ࡬࡯ࡳࡥࡨࡇ࡭ࡧ࡮ࡨࡧࡍࡥࡷ࠭ࣨ"),
  bstack1ll1_opy_ (u"࠭ࡸ࡮ࡵࡍࡥࡷࣩ࠭"),
  bstack1ll1_opy_ (u"ࠧࡹ࡯ࡻࡎࡦࡸࠧ࣪"),
  bstack1ll1_opy_ (u"ࠨ࡯ࡤࡷࡰࡉ࡯࡮࡯ࡤࡲࡩࡹࠧ࣫"),
  bstack1ll1_opy_ (u"ࠩࡰࡥࡸࡱࡂࡢࡵ࡬ࡧࡆࡻࡴࡩࠩ࣬"),
  bstack1ll1_opy_ (u"ࠪࡻࡸࡒ࡯ࡤࡣ࡯ࡗࡺࡶࡰࡰࡴࡷ࣭ࠫ"),
  bstack1ll1_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡈࡵࡲࡴࡔࡨࡷࡹࡸࡩࡤࡶ࡬ࡳࡳࡹ࣮ࠧ"),
  bstack1ll1_opy_ (u"ࠬࡧࡰࡱࡘࡨࡶࡸ࡯࡯࡯࣯ࠩ"),
  bstack1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹࡏ࡮ࡴࡧࡦࡹࡷ࡫ࡃࡦࡴࡷࡷࣰࠬ"),
  bstack1ll1_opy_ (u"ࠧࡳࡧࡶ࡭࡬ࡴࡁࡱࡲࣱࠪ"),
  bstack1ll1_opy_ (u"ࠨࡦ࡬ࡷࡦࡨ࡬ࡦࡃࡱ࡭ࡲࡧࡴࡪࡱࡱࡷࣲࠬ"),
  bstack1ll1_opy_ (u"ࠩࡦࡥࡳࡧࡲࡺࠩࣳ"),
  bstack1ll1_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫࣴ"),
  bstack1ll1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࠫࣵ"),
  bstack1ll1_opy_ (u"ࠬ࡯ࡥࠨࣶ"),
  bstack1ll1_opy_ (u"࠭ࡥࡥࡩࡨࠫࣷ"),
  bstack1ll1_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯ࠧࣸ"),
  bstack1ll1_opy_ (u"ࠨࡳࡸࡩࡺ࡫ࣹࠧ"),
  bstack1ll1_opy_ (u"ࠩ࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࣺࠫ"),
  bstack1ll1_opy_ (u"ࠪࡥࡵࡶࡓࡵࡱࡵࡩࡈࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠫࣻ"),
  bstack1ll1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡇࡦࡳࡥࡳࡣࡌࡱࡦ࡭ࡥࡊࡰ࡭ࡩࡨࡺࡩࡰࡰࠪࣼ"),
  bstack1ll1_opy_ (u"ࠬࡴࡥࡵࡹࡲࡶࡰࡒ࡯ࡨࡵࡈࡼࡨࡲࡵࡥࡧࡋࡳࡸࡺࡳࠨࣽ"),
  bstack1ll1_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡌࡰࡩࡶࡍࡳࡩ࡬ࡶࡦࡨࡌࡴࡹࡴࡴࠩࣾ"),
  bstack1ll1_opy_ (u"ࠧࡶࡲࡧࡥࡹ࡫ࡁࡱࡲࡖࡩࡹࡺࡩ࡯ࡩࡶࠫࣿ"),
  bstack1ll1_opy_ (u"ࠨࡴࡨࡷࡪࡸࡶࡦࡆࡨࡺ࡮ࡩࡥࠨऀ"),
  bstack1ll1_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩँ"),
  bstack1ll1_opy_ (u"ࠪࡷࡪࡴࡤࡌࡧࡼࡷࠬं"),
  bstack1ll1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡔࡦࡹࡳࡤࡱࡧࡩࠬः"),
  bstack1ll1_opy_ (u"ࠬࡻࡰࡥࡣࡷࡩࡎࡵࡳࡅࡧࡹ࡭ࡨ࡫ࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠨऄ"),
  bstack1ll1_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡇࡵࡥ࡫ࡲࡍࡳࡰࡥࡤࡶ࡬ࡳࡳ࠭अ"),
  bstack1ll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡁࡱࡲ࡯ࡩࡕࡧࡹࠨआ"),
  bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࠩइ"),
  bstack1ll1_opy_ (u"ࠩࡺࡨ࡮ࡵࡓࡦࡴࡹ࡭ࡨ࡫ࠧई"),
  bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬउ"),
  bstack1ll1_opy_ (u"ࠫࡵࡸࡥࡷࡧࡱࡸࡈࡸ࡯ࡴࡵࡖ࡭ࡹ࡫ࡔࡳࡣࡦ࡯࡮ࡴࡧࠨऊ"),
  bstack1ll1_opy_ (u"ࠬ࡮ࡩࡨࡪࡆࡳࡳࡺࡲࡢࡵࡷࠫऋ"),
  bstack1ll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡖࡲࡦࡨࡨࡶࡪࡴࡣࡦࡵࠪऌ"),
  bstack1ll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡓࡪ࡯ࠪऍ"),
  bstack1ll1_opy_ (u"ࠨࡵ࡬ࡱࡔࡶࡴࡪࡱࡱࡷࠬऎ"),
  bstack1ll1_opy_ (u"ࠩࡵࡩࡲࡵࡶࡦࡋࡒࡗࡆࡶࡰࡔࡧࡷࡸ࡮ࡴࡧࡴࡎࡲࡧࡦࡲࡩࡻࡣࡷ࡭ࡴࡴࠧए"),
  bstack1ll1_opy_ (u"ࠪ࡬ࡴࡹࡴࡏࡣࡰࡩࠬऐ"),
  bstack1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ऑ"),
  bstack1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࠧऒ"),
  bstack1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠬओ"),
  bstack1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩऔ"),
  bstack1ll1_opy_ (u"ࠨࡲࡤ࡫ࡪࡒ࡯ࡢࡦࡖࡸࡷࡧࡴࡦࡩࡼࠫक"),
  bstack1ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨख"),
  bstack1ll1_opy_ (u"ࠪࡸ࡮ࡳࡥࡰࡷࡷࡷࠬग"),
  bstack1ll1_opy_ (u"ࠫࡺࡴࡨࡢࡰࡧࡰࡪࡪࡐࡳࡱࡰࡴࡹࡈࡥࡩࡣࡹ࡭ࡴࡸࠧघ")
]
bstack1ll111l1l_opy_ = {
  bstack1ll1_opy_ (u"ࠬࡼࠧङ"): bstack1ll1_opy_ (u"࠭ࡶࠨच"),
  bstack1ll1_opy_ (u"ࠧࡧࠩछ"): bstack1ll1_opy_ (u"ࠨࡨࠪज"),
  bstack1ll1_opy_ (u"ࠩࡩࡳࡷࡩࡥࠨझ"): bstack1ll1_opy_ (u"ࠪࡪࡴࡸࡣࡦࠩञ"),
  bstack1ll1_opy_ (u"ࠫࡴࡴ࡬ࡺࡣࡸࡸࡴࡳࡡࡵࡧࠪट"): bstack1ll1_opy_ (u"ࠬࡵ࡮࡭ࡻࡄࡹࡹࡵ࡭ࡢࡶࡨࠫठ"),
  bstack1ll1_opy_ (u"࠭ࡦࡰࡴࡦࡩࡱࡵࡣࡢ࡮ࠪड"): bstack1ll1_opy_ (u"ࠧࡧࡱࡵࡧࡪࡲ࡯ࡤࡣ࡯ࠫढ"),
  bstack1ll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡨࡰࡵࡷࠫण"): bstack1ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡉࡱࡶࡸࠬत"),
  bstack1ll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡲࡲࡶࡹ࠭थ"): bstack1ll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡳࡷࡺࠧद"),
  bstack1ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡹࡸ࡫ࡲࠨध"): bstack1ll1_opy_ (u"࠭ࡰࡳࡱࡻࡽ࡚ࡹࡥࡳࠩन"),
  bstack1ll1_opy_ (u"ࠧࡱࡴࡲࡼࡾࡶࡡࡴࡵࠪऩ"): bstack1ll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡐࡢࡵࡶࠫप"),
  bstack1ll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡱࡴࡲࡼࡾ࡮࡯ࡴࡶࠪफ"): bstack1ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡒࡵࡳࡽࡿࡈࡰࡵࡷࠫब"),
  bstack1ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡳࡶࡴࡾࡹࡱࡱࡵࡸࠬभ"): bstack1ll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡔࡷࡵࡸࡺࡒࡲࡶࡹ࠭म"),
  bstack1ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡵࡸ࡯ࡹࡻࡸࡷࡪࡸࠧय"): bstack1ll1_opy_ (u"ࠧ࠮࡮ࡲࡧࡦࡲࡐࡳࡱࡻࡽ࡚ࡹࡥࡳࠩर"),
  bstack1ll1_opy_ (u"ࠨ࠯࡯ࡳࡨࡧ࡬ࡱࡴࡲࡼࡾࡻࡳࡦࡴࠪऱ"): bstack1ll1_opy_ (u"ࠩ࠰ࡰࡴࡩࡡ࡭ࡒࡵࡳࡽࡿࡕࡴࡧࡵࠫल"),
  bstack1ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡲࡵࡳࡽࡿࡰࡢࡵࡶࠫळ"): bstack1ll1_opy_ (u"ࠫ࠲ࡲ࡯ࡤࡣ࡯ࡔࡷࡵࡸࡺࡒࡤࡷࡸ࠭ऴ"),
  bstack1ll1_opy_ (u"ࠬ࠳࡬ࡰࡥࡤࡰࡵࡸ࡯ࡹࡻࡳࡥࡸࡹࠧव"): bstack1ll1_opy_ (u"࠭࠭࡭ࡱࡦࡥࡱࡖࡲࡰࡺࡼࡔࡦࡹࡳࠨश"),
  bstack1ll1_opy_ (u"ࠧࡣ࡫ࡱࡥࡷࡿࡰࡢࡶ࡫ࠫष"): bstack1ll1_opy_ (u"ࠨࡤ࡬ࡲࡦࡸࡹࡱࡣࡷ࡬ࠬस"),
  bstack1ll1_opy_ (u"ࠩࡳࡥࡨ࡬ࡩ࡭ࡧࠪह"): bstack1ll1_opy_ (u"ࠪ࠱ࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭ऺ"),
  bstack1ll1_opy_ (u"ࠫࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭ऻ"): bstack1ll1_opy_ (u"ࠬ࠳ࡰࡢࡥ࠰ࡪ࡮ࡲࡥࠨ़"),
  bstack1ll1_opy_ (u"࠭࠭ࡱࡣࡦ࠱࡫࡯࡬ࡦࠩऽ"): bstack1ll1_opy_ (u"ࠧ࠮ࡲࡤࡧ࠲࡬ࡩ࡭ࡧࠪा"),
  bstack1ll1_opy_ (u"ࠨ࡮ࡲ࡫࡫࡯࡬ࡦࠩि"): bstack1ll1_opy_ (u"ࠩ࡯ࡳ࡬࡬ࡩ࡭ࡧࠪी"),
  bstack1ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬु"): bstack1ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ू"),
}
bstack11lll1_opy_ = bstack1ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡨࡶࡤ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡷࡥ࠱࡫ࡹࡧ࠭ृ")
bstack1l1ll111l_opy_ = bstack1ll1_opy_ (u"࠭ࡨࡵࡶࡳ࠾࠴࠵ࡨࡶࡤ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲࡀ࠸࠱࠱ࡺࡨ࠴࡮ࡵࡣࠩॄ")
bstack1ll1l1_opy_ = {
  bstack1ll1_opy_ (u"ࠧࡤࡴ࡬ࡸ࡮ࡩࡡ࡭ࠩॅ"): 50,
  bstack1ll1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧॆ"): 40,
  bstack1ll1_opy_ (u"ࠩࡺࡥࡷࡴࡩ࡯ࡩࠪे"): 30,
  bstack1ll1_opy_ (u"ࠪ࡭ࡳ࡬࡯ࠨै"): 20,
  bstack1ll1_opy_ (u"ࠫࡩ࡫ࡢࡶࡩࠪॉ"): 10
}
DEFAULT_LOG_LEVEL = bstack1ll1l1_opy_[bstack1ll1_opy_ (u"ࠬ࡯࡮ࡧࡱࠪॊ")]
bstack1lllll111_opy_ = bstack1ll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠳ࡰࡺࡶ࡫ࡳࡳࡧࡧࡦࡰࡷ࠳ࠬो")
bstack1l1l1l_opy_ = bstack1ll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠳ࡰࡺࡶ࡫ࡳࡳࡧࡧࡦࡰࡷ࠳ࠬौ")
bstack1lllll11_opy_ = bstack1ll1_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵्ࠧ")
bstack1l11l1ll1_opy_ = bstack1ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵ࠯ࡳࡽࡹ࡮࡯࡯ࡣࡪࡩࡳࡺ࠯ࠨॎ")
bstack1ll1ll1ll_opy_ = [bstack1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡘࡗࡊࡘࡎࡂࡏࡈࠫॏ"), bstack1ll1_opy_ (u"ࠫ࡞ࡕࡕࡓࡡࡘࡗࡊࡘࡎࡂࡏࡈࠫॐ")]
bstack111111ll_opy_ = [bstack1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆࡉࡃࡆࡕࡖࡣࡐࡋ࡙ࠨ॑"), bstack1ll1_opy_ (u"࡙࠭ࡐࡗࡕࡣࡆࡉࡃࡆࡕࡖࡣࡐࡋ࡙ࠨ॒")]
bstack1l11l1lll_opy_ = [
  bstack1ll1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡒࡦࡳࡥࠨ॓"),
  bstack1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠪ॔"),
  bstack1ll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭ॕ"),
  bstack1ll1_opy_ (u"ࠪࡲࡪࡽࡃࡰ࡯ࡰࡥࡳࡪࡔࡪ࡯ࡨࡳࡺࡺࠧॖ"),
  bstack1ll1_opy_ (u"ࠫࡦࡶࡰࠨॗ"),
  bstack1ll1_opy_ (u"ࠬࡻࡤࡪࡦࠪक़"),
  bstack1ll1_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࠨख़"),
  bstack1ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࡫ࠧग़"),
  bstack1ll1_opy_ (u"ࠨࡱࡵ࡭ࡪࡴࡴࡢࡶ࡬ࡳࡳ࠭ज़"),
  bstack1ll1_opy_ (u"ࠩࡤࡹࡹࡵࡗࡦࡤࡹ࡭ࡪࡽࠧड़"),
  bstack1ll1_opy_ (u"ࠪࡲࡴࡘࡥࡴࡧࡷࠫढ़"), bstack1ll1_opy_ (u"ࠫ࡫ࡻ࡬࡭ࡔࡨࡷࡪࡺࠧफ़"),
  bstack1ll1_opy_ (u"ࠬࡩ࡬ࡦࡣࡵࡗࡾࡹࡴࡦ࡯ࡉ࡭ࡱ࡫ࡳࠨय़"),
  bstack1ll1_opy_ (u"࠭ࡥࡷࡧࡱࡸ࡙࡯࡭ࡪࡰࡪࡷࠬॠ"),
  bstack1ll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡐࡦࡴࡩࡳࡷࡳࡡ࡯ࡥࡨࡐࡴ࡭ࡧࡪࡰࡪࠫॡ"),
  bstack1ll1_opy_ (u"ࠨࡱࡷ࡬ࡪࡸࡁࡱࡲࡶࠫॢ"),
  bstack1ll1_opy_ (u"ࠩࡳࡶ࡮ࡴࡴࡑࡣࡪࡩࡘࡵࡵࡳࡥࡨࡓࡳࡌࡩ࡯ࡦࡉࡥ࡮ࡲࡵࡳࡧࠪॣ"),
  bstack1ll1_opy_ (u"ࠪࡥࡵࡶࡁࡤࡶ࡬ࡺ࡮ࡺࡹࠨ।"), bstack1ll1_opy_ (u"ࠫࡦࡶࡰࡑࡣࡦ࡯ࡦ࡭ࡥࠨ॥"), bstack1ll1_opy_ (u"ࠬࡧࡰࡱ࡙ࡤ࡭ࡹࡇࡣࡵ࡫ࡹ࡭ࡹࡿࠧ०"), bstack1ll1_opy_ (u"࠭ࡡࡱࡲ࡚ࡥ࡮ࡺࡐࡢࡥ࡮ࡥ࡬࡫ࠧ१"), bstack1ll1_opy_ (u"ࠧࡢࡲࡳ࡛ࡦ࡯ࡴࡅࡷࡵࡥࡹ࡯࡯࡯ࠩ२"),
  bstack1ll1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡓࡧࡤࡨࡾ࡚ࡩ࡮ࡧࡲࡹࡹ࠭३"),
  bstack1ll1_opy_ (u"ࠩࡤࡰࡱࡵࡷࡕࡧࡶࡸࡕࡧࡣ࡬ࡣࡪࡩࡸ࠭४"),
  bstack1ll1_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࡇࡴࡼࡥࡳࡣࡪࡩࠬ५"), bstack1ll1_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡈࡵࡶࡦࡴࡤ࡫ࡪࡋ࡮ࡥࡋࡱࡸࡪࡴࡴࠨ६"),
  bstack1ll1_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩࡊࡥࡷ࡫ࡦࡩࡗ࡫ࡡࡥࡻࡗ࡭ࡲ࡫࡯ࡶࡶࠪ७"),
  bstack1ll1_opy_ (u"࠭ࡡࡥࡤࡓࡳࡷࡺࠧ८"),
  bstack1ll1_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࡅࡧࡹ࡭ࡨ࡫ࡓࡰࡥ࡮ࡩࡹ࠭९"),
  bstack1ll1_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࡋࡱࡷࡹࡧ࡬࡭ࡖ࡬ࡱࡪࡵࡵࡵࠩ॰"),
  bstack1ll1_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡌࡲࡸࡺࡡ࡭࡮ࡓࡥࡹ࡮ࠧॱ"),
  bstack1ll1_opy_ (u"ࠪࡥࡻࡪࠧॲ"), bstack1ll1_opy_ (u"ࠫࡦࡼࡤࡍࡣࡸࡲࡨ࡮ࡔࡪ࡯ࡨࡳࡺࡺࠧॳ"), bstack1ll1_opy_ (u"ࠬࡧࡶࡥࡔࡨࡥࡩࡿࡔࡪ࡯ࡨࡳࡺࡺࠧॴ"), bstack1ll1_opy_ (u"࠭ࡡࡷࡦࡄࡶ࡬ࡹࠧॵ"),
  bstack1ll1_opy_ (u"ࠧࡶࡵࡨࡏࡪࡿࡳࡵࡱࡵࡩࠬॶ"), bstack1ll1_opy_ (u"ࠨ࡭ࡨࡽࡸࡺ࡯ࡳࡧࡓࡥࡹ࡮ࠧॷ"), bstack1ll1_opy_ (u"ࠩ࡮ࡩࡾࡹࡴࡰࡴࡨࡔࡦࡹࡳࡸࡱࡵࡨࠬॸ"),
  bstack1ll1_opy_ (u"ࠪ࡯ࡪࡿࡁ࡭࡫ࡤࡷࠬॹ"), bstack1ll1_opy_ (u"ࠫࡰ࡫ࡹࡑࡣࡶࡷࡼࡵࡲࡥࠩॺ"),
  bstack1ll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡩࡸࡩࡷࡧࡵࡉࡽ࡫ࡣࡶࡶࡤࡦࡱ࡫ࠧॻ"), bstack1ll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡪࡲࡪࡸࡨࡶࡆࡸࡧࡴࠩॼ"), bstack1ll1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡋࡸࡦࡥࡸࡸࡦࡨ࡬ࡦࡆ࡬ࡶࠬॽ"), bstack1ll1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡥࡴ࡬ࡺࡪࡸࡃࡩࡴࡲࡱࡪࡓࡡࡱࡲ࡬ࡲ࡬ࡌࡩ࡭ࡧࠪॾ"), bstack1ll1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡖࡵࡨࡗࡾࡹࡴࡦ࡯ࡈࡼࡪࡩࡵࡵࡣࡥࡰࡪ࠭ॿ"),
  bstack1ll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡧࡶ࡮ࡼࡥࡳࡒࡲࡶࡹ࠭ঀ"), bstack1ll1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡨࡷ࡯ࡶࡦࡴࡓࡳࡷࡺࡳࠨঁ"),
  bstack1ll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡩࡸࡩࡷࡧࡵࡈ࡮ࡹࡡࡣ࡮ࡨࡆࡺ࡯࡬ࡥࡅ࡫ࡩࡨࡱࠧং"),
  bstack1ll1_opy_ (u"࠭ࡡࡶࡶࡲ࡛ࡪࡨࡶࡪࡧࡺࡘ࡮ࡳࡥࡰࡷࡷࠫঃ"),
  bstack1ll1_opy_ (u"ࠧࡪࡰࡷࡩࡳࡺࡁࡤࡶ࡬ࡳࡳ࠭঄"), bstack1ll1_opy_ (u"ࠨ࡫ࡱࡸࡪࡴࡴࡄࡣࡷࡩ࡬ࡵࡲࡺࠩঅ"), bstack1ll1_opy_ (u"ࠩ࡬ࡲࡹ࡫࡮ࡵࡈ࡯ࡥ࡬ࡹࠧআ"), bstack1ll1_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡤࡰࡎࡴࡴࡦࡰࡷࡅࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ই"),
  bstack1ll1_opy_ (u"ࠫࡩࡵ࡮ࡵࡕࡷࡳࡵࡇࡰࡱࡑࡱࡖࡪࡹࡥࡵࠩঈ"),
  bstack1ll1_opy_ (u"ࠬࡻ࡮ࡪࡥࡲࡨࡪࡑࡥࡺࡤࡲࡥࡷࡪࠧউ"), bstack1ll1_opy_ (u"࠭ࡲࡦࡵࡨࡸࡐ࡫ࡹࡣࡱࡤࡶࡩ࠭ঊ"),
  bstack1ll1_opy_ (u"ࠧ࡯ࡱࡖ࡭࡬ࡴࠧঋ"),
  bstack1ll1_opy_ (u"ࠨ࡫ࡪࡲࡴࡸࡥࡖࡰ࡬ࡱࡵࡵࡲࡵࡣࡱࡸ࡛࡯ࡥࡸࡵࠪঌ"),
  bstack1ll1_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡲࡩࡸ࡯ࡪࡦ࡚ࡥࡹࡩࡨࡦࡴࡶࠫ঍"),
  bstack1ll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ঎"),
  bstack1ll1_opy_ (u"ࠫࡷ࡫ࡣࡳࡧࡤࡸࡪࡉࡨࡳࡱࡰࡩࡉࡸࡩࡷࡧࡵࡗࡪࡹࡳࡪࡱࡱࡷࠬএ"),
  bstack1ll1_opy_ (u"ࠬࡴࡡࡵ࡫ࡹࡩ࡜࡫ࡢࡔࡥࡵࡩࡪࡴࡳࡩࡱࡷࠫঐ"),
  bstack1ll1_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࡓࡤࡴࡨࡩࡳࡹࡨࡰࡶࡓࡥࡹ࡮ࠧ঑"),
  bstack1ll1_opy_ (u"ࠧ࡯ࡧࡷࡻࡴࡸ࡫ࡔࡲࡨࡩࡩ࠭঒"),
  bstack1ll1_opy_ (u"ࠨࡩࡳࡷࡊࡴࡡࡣ࡮ࡨࡨࠬও"),
  bstack1ll1_opy_ (u"ࠩ࡬ࡷࡍ࡫ࡡࡥ࡮ࡨࡷࡸ࠭ঔ"),
  bstack1ll1_opy_ (u"ࠪࡥࡩࡨࡅࡹࡧࡦࡘ࡮ࡳࡥࡰࡷࡷࠫক"),
  bstack1ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡨࡗࡨࡸࡩࡱࡶࠪখ"),
  bstack1ll1_opy_ (u"ࠬࡹ࡫ࡪࡲࡇࡩࡻ࡯ࡣࡦࡋࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡥࡹ࡯࡯࡯ࠩগ"),
  bstack1ll1_opy_ (u"࠭ࡡࡶࡶࡲࡋࡷࡧ࡮ࡵࡒࡨࡶࡲ࡯ࡳࡴ࡫ࡲࡲࡸ࠭ঘ"),
  bstack1ll1_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࡏࡣࡷࡹࡷࡧ࡬ࡐࡴ࡬ࡩࡳࡺࡡࡵ࡫ࡲࡲࠬঙ"),
  bstack1ll1_opy_ (u"ࠨࡵࡼࡷࡹ࡫࡭ࡑࡱࡵࡸࠬচ"),
  bstack1ll1_opy_ (u"ࠩࡵࡩࡲࡵࡴࡦࡃࡧࡦࡍࡵࡳࡵࠩছ"),
  bstack1ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡖࡰ࡯ࡳࡨࡱࠧজ"), bstack1ll1_opy_ (u"ࠫࡺࡴ࡬ࡰࡥ࡮ࡘࡾࡶࡥࠨঝ"), bstack1ll1_opy_ (u"ࠬࡻ࡮࡭ࡱࡦ࡯ࡐ࡫ࡹࠨঞ"),
  bstack1ll1_opy_ (u"࠭ࡡࡶࡶࡲࡐࡦࡻ࡮ࡤࡪࠪট"),
  bstack1ll1_opy_ (u"ࠧࡴ࡭࡬ࡴࡑࡵࡧࡤࡣࡷࡇࡦࡶࡴࡶࡴࡨࠫঠ"),
  bstack1ll1_opy_ (u"ࠨࡷࡱ࡭ࡳࡹࡴࡢ࡮࡯ࡓࡹ࡮ࡥࡳࡒࡤࡧࡰࡧࡧࡦࡵࠪড"),
  bstack1ll1_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧ࡚࡭ࡳࡪ࡯ࡸࡃࡱ࡭ࡲࡧࡴࡪࡱࡱࠫঢ"),
  bstack1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡖࡲࡳࡱࡹࡖࡦࡴࡶ࡭ࡴࡴࠧণ"),
  bstack1ll1_opy_ (u"ࠫࡪࡴࡦࡰࡴࡦࡩࡆࡶࡰࡊࡰࡶࡸࡦࡲ࡬ࠨত"),
  bstack1ll1_opy_ (u"ࠬ࡫࡮ࡴࡷࡵࡩ࡜࡫ࡢࡷ࡫ࡨࡻࡸࡎࡡࡷࡧࡓࡥ࡬࡫ࡳࠨথ"), bstack1ll1_opy_ (u"࠭ࡷࡦࡤࡹ࡭ࡪࡽࡄࡦࡸࡷࡳࡴࡲࡳࡑࡱࡵࡸࠬদ"), bstack1ll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡗࡦࡤࡹ࡭ࡪࡽࡄࡦࡶࡤ࡭ࡱࡹࡃࡰ࡮࡯ࡩࡨࡺࡩࡰࡰࠪধ"),
  bstack1ll1_opy_ (u"ࠨࡴࡨࡱࡴࡺࡥࡂࡲࡳࡷࡈࡧࡣࡩࡧࡏ࡭ࡲ࡯ࡴࠨন"),
  bstack1ll1_opy_ (u"ࠩࡦࡥࡱ࡫࡮ࡥࡣࡵࡊࡴࡸ࡭ࡢࡶࠪ঩"),
  bstack1ll1_opy_ (u"ࠪࡦࡺࡴࡤ࡭ࡧࡌࡨࠬপ"),
  bstack1ll1_opy_ (u"ࠫࡱࡧࡵ࡯ࡥ࡫ࡘ࡮ࡳࡥࡰࡷࡷࠫফ"),
  bstack1ll1_opy_ (u"ࠬࡲ࡯ࡤࡣࡷ࡭ࡴࡴࡓࡦࡴࡹ࡭ࡨ࡫ࡳࡆࡰࡤࡦࡱ࡫ࡤࠨব"), bstack1ll1_opy_ (u"࠭࡬ࡰࡥࡤࡸ࡮ࡵ࡮ࡔࡧࡵࡺ࡮ࡩࡥࡴࡃࡸࡸ࡭ࡵࡲࡪࡼࡨࡨࠬভ"),
  bstack1ll1_opy_ (u"ࠧࡢࡷࡷࡳࡆࡩࡣࡦࡲࡷࡅࡱ࡫ࡲࡵࡵࠪম"), bstack1ll1_opy_ (u"ࠨࡣࡸࡸࡴࡊࡩࡴ࡯࡬ࡷࡸࡇ࡬ࡦࡴࡷࡷࠬয"),
  bstack1ll1_opy_ (u"ࠩࡱࡥࡹ࡯ࡶࡦࡋࡱࡷࡹࡸࡵ࡮ࡧࡱࡸࡸࡒࡩࡣࠩর"),
  bstack1ll1_opy_ (u"ࠪࡲࡦࡺࡩࡷࡧ࡚ࡩࡧ࡚ࡡࡱࠩ঱"),
  bstack1ll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬ࡍࡳ࡯ࡴࡪࡣ࡯࡙ࡷࡲࠧল"), bstack1ll1_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭ࡆࡲ࡬ࡰࡹࡓࡳࡵࡻࡰࡴࠩ঳"), bstack1ll1_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮ࡏࡧ࡯ࡱࡵࡩࡋࡸࡡࡶࡦ࡚ࡥࡷࡴࡩ࡯ࡩࠪ঴"), bstack1ll1_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯ࡏࡱࡧࡱࡐ࡮ࡴ࡫ࡴࡋࡱࡆࡦࡩ࡫ࡨࡴࡲࡹࡳࡪࠧ঵"),
  bstack1ll1_opy_ (u"ࠨ࡭ࡨࡩࡵࡑࡥࡺࡅ࡫ࡥ࡮ࡴࡳࠨশ"),
  bstack1ll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡪࡼࡤࡦࡱ࡫ࡓࡵࡴ࡬ࡲ࡬ࡹࡄࡪࡴࠪষ"),
  bstack1ll1_opy_ (u"ࠪࡴࡷࡵࡣࡦࡵࡶࡅࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭স"),
  bstack1ll1_opy_ (u"ࠫ࡮ࡴࡴࡦࡴࡎࡩࡾࡊࡥ࡭ࡣࡼࠫহ"),
  bstack1ll1_opy_ (u"ࠬࡹࡨࡰࡹࡌࡓࡘࡒ࡯ࡨࠩ঺"),
  bstack1ll1_opy_ (u"࠭ࡳࡦࡰࡧࡏࡪࡿࡓࡵࡴࡤࡸࡪ࡭ࡹࠨ঻"),
  bstack1ll1_opy_ (u"ࠧࡸࡧࡥ࡯࡮ࡺࡒࡦࡵࡳࡳࡳࡹࡥࡕ࡫ࡰࡩࡴࡻࡴࠨ়"), bstack1ll1_opy_ (u"ࠨࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸ࡜ࡧࡩࡵࡖ࡬ࡱࡪࡵࡵࡵࠩঽ"),
  bstack1ll1_opy_ (u"ࠩࡵࡩࡲࡵࡴࡦࡆࡨࡦࡺ࡭ࡐࡳࡱࡻࡽࠬা"),
  bstack1ll1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡄࡷࡾࡴࡣࡆࡺࡨࡧࡺࡺࡥࡇࡴࡲࡱࡍࡺࡴࡱࡵࠪি"),
  bstack1ll1_opy_ (u"ࠫࡸࡱࡩࡱࡎࡲ࡫ࡈࡧࡰࡵࡷࡵࡩࠬী"),
  bstack1ll1_opy_ (u"ࠬࡽࡥࡣ࡭࡬ࡸࡉ࡫ࡢࡶࡩࡓࡶࡴࡾࡹࡑࡱࡵࡸࠬু"),
  bstack1ll1_opy_ (u"࠭ࡦࡶ࡮࡯ࡇࡴࡴࡴࡦࡺࡷࡐ࡮ࡹࡴࠨূ"),
  bstack1ll1_opy_ (u"ࠧࡸࡣ࡬ࡸࡋࡵࡲࡂࡲࡳࡗࡨࡸࡩࡱࡶࠪৃ"),
  bstack1ll1_opy_ (u"ࠨࡹࡨࡦࡻ࡯ࡥࡸࡅࡲࡲࡳ࡫ࡣࡵࡔࡨࡸࡷ࡯ࡥࡴࠩৄ"),
  bstack1ll1_opy_ (u"ࠩࡤࡴࡵࡔࡡ࡮ࡧࠪ৅"),
  bstack1ll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡖࡗࡑࡉࡥࡳࡶࠪ৆"),
  bstack1ll1_opy_ (u"ࠫࡹࡧࡰࡘ࡫ࡷ࡬ࡘ࡮࡯ࡳࡶࡓࡶࡪࡹࡳࡅࡷࡵࡥࡹ࡯࡯࡯ࠩে"),
  bstack1ll1_opy_ (u"ࠬࡹࡣࡢ࡮ࡨࡊࡦࡩࡴࡰࡴࠪৈ"),
  bstack1ll1_opy_ (u"࠭ࡷࡥࡣࡏࡳࡨࡧ࡬ࡑࡱࡵࡸࠬ৉"),
  bstack1ll1_opy_ (u"ࠧࡴࡪࡲࡻ࡝ࡩ࡯ࡥࡧࡏࡳ࡬࠭৊"),
  bstack1ll1_opy_ (u"ࠨ࡫ࡲࡷࡎࡴࡳࡵࡣ࡯ࡰࡕࡧࡵࡴࡧࠪো"),
  bstack1ll1_opy_ (u"ࠩࡻࡧࡴࡪࡥࡄࡱࡱࡪ࡮࡭ࡆࡪ࡮ࡨࠫৌ"),
  bstack1ll1_opy_ (u"ࠪ࡯ࡪࡿࡣࡩࡣ࡬ࡲࡕࡧࡳࡴࡹࡲࡶࡩ্࠭"),
  bstack1ll1_opy_ (u"ࠫࡺࡹࡥࡑࡴࡨࡦࡺ࡯࡬ࡵ࡙ࡇࡅࠬৎ"),
  bstack1ll1_opy_ (u"ࠬࡶࡲࡦࡸࡨࡲࡹ࡝ࡄࡂࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠭৏"),
  bstack1ll1_opy_ (u"࠭ࡷࡦࡤࡇࡶ࡮ࡼࡥࡳࡃࡪࡩࡳࡺࡕࡳ࡮ࠪ৐"),
  bstack1ll1_opy_ (u"ࠧ࡬ࡧࡼࡧ࡭ࡧࡩ࡯ࡒࡤࡸ࡭࠭৑"),
  bstack1ll1_opy_ (u"ࠨࡷࡶࡩࡓ࡫ࡷࡘࡆࡄࠫ৒"),
  bstack1ll1_opy_ (u"ࠩࡺࡨࡦࡒࡡࡶࡰࡦ࡬࡙࡯࡭ࡦࡱࡸࡸࠬ৓"), bstack1ll1_opy_ (u"ࠪࡻࡩࡧࡃࡰࡰࡱࡩࡨࡺࡩࡰࡰࡗ࡭ࡲ࡫࡯ࡶࡶࠪ৔"),
  bstack1ll1_opy_ (u"ࠫࡽࡩ࡯ࡥࡧࡒࡶ࡬ࡏࡤࠨ৕"), bstack1ll1_opy_ (u"ࠬࡾࡣࡰࡦࡨࡗ࡮࡭࡮ࡪࡰࡪࡍࡩ࠭৖"),
  bstack1ll1_opy_ (u"࠭ࡵࡱࡦࡤࡸࡪࡪࡗࡅࡃࡅࡹࡳࡪ࡬ࡦࡋࡧࠫৗ"),
  bstack1ll1_opy_ (u"ࠧࡳࡧࡶࡩࡹࡕ࡮ࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡶࡹࡕ࡮࡭ࡻࠪ৘"),
  bstack1ll1_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡖ࡬ࡱࡪࡵࡵࡵࡵࠪ৙"),
  bstack1ll1_opy_ (u"ࠩࡺࡨࡦ࡙ࡴࡢࡴࡷࡹࡵࡘࡥࡵࡴ࡬ࡩࡸ࠭৚"), bstack1ll1_opy_ (u"ࠪࡻࡩࡧࡓࡵࡣࡵࡸࡺࡶࡒࡦࡶࡵࡽࡎࡴࡴࡦࡴࡹࡥࡱ࠭৛"),
  bstack1ll1_opy_ (u"ࠫࡨࡵ࡮࡯ࡧࡦࡸࡍࡧࡲࡥࡹࡤࡶࡪࡑࡥࡺࡤࡲࡥࡷࡪࠧড়"),
  bstack1ll1_opy_ (u"ࠬࡳࡡࡹࡖࡼࡴ࡮ࡴࡧࡇࡴࡨࡵࡺ࡫࡮ࡤࡻࠪঢ়"),
  bstack1ll1_opy_ (u"࠭ࡳࡪ࡯ࡳࡰࡪࡏࡳࡗ࡫ࡶ࡭ࡧࡲࡥࡄࡪࡨࡧࡰ࠭৞"),
  bstack1ll1_opy_ (u"ࠧࡶࡵࡨࡇࡦࡸࡴࡩࡣࡪࡩࡘࡹ࡬ࠨয়"),
  bstack1ll1_opy_ (u"ࠨࡵ࡫ࡳࡺࡲࡤࡖࡵࡨࡗ࡮ࡴࡧ࡭ࡧࡷࡳࡳ࡚ࡥࡴࡶࡐࡥࡳࡧࡧࡦࡴࠪৠ"),
  bstack1ll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡊ࡙ࡇࡔࠬৡ"),
  bstack1ll1_opy_ (u"ࠪࡥࡱࡲ࡯ࡸࡖࡲࡹࡨ࡮ࡉࡥࡇࡱࡶࡴࡲ࡬ࠨৢ"),
  bstack1ll1_opy_ (u"ࠫ࡮࡭࡮ࡰࡴࡨࡌ࡮ࡪࡤࡦࡰࡄࡴ࡮ࡖ࡯࡭࡫ࡦࡽࡊࡸࡲࡰࡴࠪৣ"),
  bstack1ll1_opy_ (u"ࠬࡳ࡯ࡤ࡭ࡏࡳࡨࡧࡴࡪࡱࡱࡅࡵࡶࠧ৤"),
  bstack1ll1_opy_ (u"࠭࡬ࡰࡩࡦࡥࡹࡌ࡯ࡳ࡯ࡤࡸࠬ৥"), bstack1ll1_opy_ (u"ࠧ࡭ࡱࡪࡧࡦࡺࡆࡪ࡮ࡷࡩࡷ࡙ࡰࡦࡥࡶࠫ০"),
  bstack1ll1_opy_ (u"ࠨࡣ࡯ࡰࡴࡽࡄࡦ࡮ࡤࡽࡆࡪࡢࠨ১")
]
bstack1l1llll1_opy_ = bstack1ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡥࡵ࡯࠭ࡤ࡮ࡲࡹࡩ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥ࠰ࡷࡳࡰࡴࡧࡤࠨ২")
bstack1l1l1l1_opy_ = [bstack1ll1_opy_ (u"ࠪ࠲ࡦࡶ࡫ࠨ৩"), bstack1ll1_opy_ (u"ࠫ࠳ࡧࡡࡣࠩ৪"), bstack1ll1_opy_ (u"ࠬ࠴ࡩࡱࡣࠪ৫")]
bstack1l11l1l1l_opy_ = [bstack1ll1_opy_ (u"࠭ࡩࡥࠩ৬"), bstack1ll1_opy_ (u"ࠧࡱࡣࡷ࡬ࠬ৭"), bstack1ll1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡠ࡫ࡧࠫ৮"), bstack1ll1_opy_ (u"ࠩࡶ࡬ࡦࡸࡥࡢࡤ࡯ࡩࡤ࡯ࡤࠨ৯")]
bstack11l1ll11_opy_ = {
  bstack1ll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪৰ"): bstack1ll1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩৱ"),
  bstack1ll1_opy_ (u"ࠬ࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭৲"): bstack1ll1_opy_ (u"࠭࡭ࡰࡼ࠽ࡪ࡮ࡸࡥࡧࡱࡻࡓࡵࡺࡩࡰࡰࡶࠫ৳"),
  bstack1ll1_opy_ (u"ࠧࡦࡦࡪࡩࡔࡶࡴࡪࡱࡱࡷࠬ৴"): bstack1ll1_opy_ (u"ࠨ࡯ࡶ࠾ࡪࡪࡧࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩ৵"),
  bstack1ll1_opy_ (u"ࠩ࡬ࡩࡔࡶࡴࡪࡱࡱࡷࠬ৶"): bstack1ll1_opy_ (u"ࠪࡷࡪࡀࡩࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩ৷"),
  bstack1ll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬ࡓࡵࡺࡩࡰࡰࡶࠫ৸"): bstack1ll1_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭৹")
}
bstack11111l11_opy_ = [
  bstack1ll1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ৺"),
  bstack1ll1_opy_ (u"ࠧ࡮ࡱࡽ࠾࡫࡯ࡲࡦࡨࡲࡼࡔࡶࡴࡪࡱࡱࡷࠬ৻"),
  bstack1ll1_opy_ (u"ࠨ࡯ࡶ࠾ࡪࡪࡧࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩৼ"),
  bstack1ll1_opy_ (u"ࠩࡶࡩ࠿࡯ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ৽"),
  bstack1ll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫࠱ࡳࡵࡺࡩࡰࡰࡶࠫ৾"),
]
bstack11111l1l_opy_ = bstack1llll_opy_ + bstack1lll1l1l_opy_ + bstack1l11l1lll_opy_
bstack1lll111ll_opy_ = [
  bstack1ll1_opy_ (u"ࠫࡣࡲ࡯ࡤࡣ࡯࡬ࡴࡹࡴࠥࠩ৿"),
  bstack1ll1_opy_ (u"ࠬࡤࡢࡴ࠯࡯ࡳࡨࡧ࡬࠯ࡥࡲࡱࠩ࠭਀"),
  bstack1ll1_opy_ (u"࠭࡞࠲࠴࠺࠲ࠬਁ"),
  bstack1ll1_opy_ (u"ࠧ࡟࠳࠳࠲ࠬਂ"),
  bstack1ll1_opy_ (u"ࠨࡠ࠴࠻࠷࠴࠱࡜࠸࠰࠽ࡢ࠴ࠧਃ"),
  bstack1ll1_opy_ (u"ࠩࡡ࠵࠼࠸࠮࠳࡝࠳࠱࠾ࡣ࠮ࠨ਄"),
  bstack1ll1_opy_ (u"ࠪࡢ࠶࠽࠲࠯࠵࡞࠴࠲࠷࡝࠯ࠩਅ"),
  bstack1ll1_opy_ (u"ࠫࡣ࠷࠹࠳࠰࠴࠺࠽࠴ࠧਆ")
]
bstack1l1l11_opy_ = bstack1ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡡࡱ࡫࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡻࡾࠩਇ")
bstack1llll11l_opy_ = bstack1ll1_opy_ (u"࠭ࡳࡥ࡭࠲ࡺ࠶࠵ࡥࡷࡧࡱࡸࠬਈ")
bstack1lllllll_opy_ = [ bstack1ll1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩਉ") ]
bstack1l1l1l111_opy_ = [ bstack1ll1_opy_ (u"ࠨࡣࡳࡴ࠲ࡧࡵࡵࡱࡰࡥࡹ࡫ࠧਊ") ]
bstack11ll111l_opy_ = [ bstack1ll1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ਋") ]
bstack1l11l1l1_opy_ = bstack1ll1_opy_ (u"ࠪࡗࡉࡑࡓࡦࡶࡸࡴࠬ਌")
bstack1l1llll1l_opy_ = bstack1ll1_opy_ (u"ࠫࡘࡊࡋࡕࡧࡶࡸࡆࡺࡴࡦ࡯ࡳࡸࡪࡪࠧ਍")
bstack1lll1l111_opy_ = bstack1ll1_opy_ (u"࡙ࠬࡄࡌࡖࡨࡷࡹ࡙ࡵࡤࡥࡨࡷࡸ࡬ࡵ࡭ࠩ਎")
bstack1lllll1l_opy_ = bstack1ll1_opy_ (u"࠭࠴࠯࠲࠱࠴ࠬਏ")
bstack1l1l1llll_opy_ = [
  bstack1ll1_opy_ (u"ࠧࡆࡔࡕࡣࡋࡇࡉࡍࡇࡇࠫਐ"),
  bstack1ll1_opy_ (u"ࠨࡇࡕࡖࡤ࡚ࡉࡎࡇࡇࡣࡔ࡛ࡔࠨ਑"),
  bstack1ll1_opy_ (u"ࠩࡈࡖࡗࡥࡂࡍࡑࡆࡏࡊࡊ࡟ࡃ࡛ࡢࡇࡑࡏࡅࡏࡖࠪ਒"),
  bstack1ll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡏࡇࡗ࡛ࡔࡘࡋࡠࡅࡋࡅࡓࡍࡅࡅࠩਓ"),
  bstack1ll1_opy_ (u"ࠫࡊࡘࡒࡠࡕࡒࡇࡐࡋࡔࡠࡐࡒࡘࡤࡉࡏࡏࡐࡈࡇ࡙ࡋࡄࠨਔ"),
  bstack1ll1_opy_ (u"ࠬࡋࡒࡓࡡࡆࡓࡓࡔࡅࡄࡖࡌࡓࡓࡥࡃࡍࡑࡖࡉࡉ࠭ਕ"),
  bstack1ll1_opy_ (u"࠭ࡅࡓࡔࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡓࡇࡖࡉ࡙࠭ਖ"),
  bstack1ll1_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡔࡈࡊ࡚࡙ࡅࡅࠩਗ"),
  bstack1ll1_opy_ (u"ࠨࡇࡕࡖࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡄࡆࡔࡘࡔࡆࡆࠪਘ"),
  bstack1ll1_opy_ (u"ࠩࡈࡖࡗࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆࠪਙ"),
  bstack1ll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡏࡃࡐࡉࡤࡔࡏࡕࡡࡕࡉࡘࡕࡌࡗࡇࡇࠫਚ"),
  bstack1ll1_opy_ (u"ࠫࡊࡘࡒࡠࡃࡇࡈࡗࡋࡓࡔࡡࡌࡒ࡛ࡇࡌࡊࡆࠪਛ"),
  bstack1ll1_opy_ (u"ࠬࡋࡒࡓࡡࡄࡈࡉࡘࡅࡔࡕࡢ࡙ࡓࡘࡅࡂࡅࡋࡅࡇࡒࡅࠨਜ"),
  bstack1ll1_opy_ (u"࠭ࡅࡓࡔࡢࡘ࡚ࡔࡎࡆࡎࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡇࡃࡌࡐࡊࡊࠧਝ"),
  bstack1ll1_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡖࡌࡑࡊࡊ࡟ࡐࡗࡗࠫਞ"),
  bstack1ll1_opy_ (u"ࠨࡇࡕࡖࡤ࡙ࡏࡄࡍࡖࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡈࡄࡍࡑࡋࡄࠨਟ"),
  bstack1ll1_opy_ (u"ࠩࡈࡖࡗࡥࡓࡐࡅࡎࡗࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡋࡓࡘ࡚࡟ࡖࡐࡕࡉࡆࡉࡈࡂࡄࡏࡉࠬਠ"),
  bstack1ll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡑࡔࡒ࡜࡞ࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆࠪਡ"),
  bstack1ll1_opy_ (u"ࠫࡊࡘࡒࡠࡐࡄࡑࡊࡥࡎࡐࡖࡢࡖࡊ࡙ࡏࡍࡘࡈࡈࠬਢ"),
  bstack1ll1_opy_ (u"ࠬࡋࡒࡓࡡࡑࡅࡒࡋ࡟ࡓࡇࡖࡓࡑ࡛ࡔࡊࡑࡑࡣࡋࡇࡉࡍࡇࡇࠫਣ"),
  bstack1ll1_opy_ (u"࠭ࡅࡓࡔࡢࡑࡆࡔࡄࡂࡖࡒࡖ࡞ࡥࡐࡓࡑ࡛࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬਤ"),
]
bstack1l1l1l1ll_opy_ = bstack1ll1_opy_ (u"ࠧࡔࡧࡷࡸ࡮ࡴࡧࠡࡷࡳࠤ࡫ࡵࡲࠡࡄࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠬࠡࡷࡶ࡭ࡳ࡭ࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭࠽ࠤࢀࢃࠧਥ")
bstack1l1llll_opy_ = bstack1ll1_opy_ (u"ࠨࡅࡲࡱࡵࡲࡥࡵࡧࡧࠤࡸ࡫ࡴࡶࡲࠤࠫਦ")
bstack11lll11_opy_ = bstack1ll1_opy_ (u"ࠩࡓࡥࡷࡹࡥࡥࠢࡦࡳࡳ࡬ࡩࡨࠢࡩ࡭ࡱ࡫࠺ࠡࡽࢀࠫਧ")
bstack1l1ll1_opy_ = bstack1ll1_opy_ (u"ࠪࡗࡦࡴࡩࡵ࡫ࡽࡩࡩࠦࡣࡰࡰࡩ࡭࡬ࠦࡦࡪ࡮ࡨ࠾ࠥࢁࡽࠨਨ")
bstack1lll1ll_opy_ = bstack1ll1_opy_ (u"࡚ࠫࡹࡩ࡯ࡩࠣ࡬ࡺࡨࠠࡶࡴ࡯࠾ࠥࢁࡽࠨ਩")
bstack11lll11l_opy_ = bstack1ll1_opy_ (u"࡙ࠬࡥࡴࡵ࡬ࡳࡳࠦࡳࡵࡣࡵࡸࡪࡪࠠࡸ࡫ࡷ࡬ࠥ࡯ࡤ࠻ࠢࡾࢁࠬਪ")
bstack1l1l11l1_opy_ = bstack1ll1_opy_ (u"࠭ࡒࡦࡥࡨ࡭ࡻ࡫ࡤࠡ࡫ࡱࡸࡪࡸࡲࡶࡲࡷ࠰ࠥ࡫ࡸࡪࡶ࡬ࡲ࡬࠭ਫ")
bstack11l11_opy_ = bstack1ll1_opy_ (u"ࠧࡑ࡮ࡨࡥࡸ࡫ࠠࡪࡰࡶࡸࡦࡲ࡬ࠡࡵࡨࡰࡪࡴࡩࡶ࡯ࠣࡸࡴࠦࡲࡶࡰࠣࡸࡪࡹࡴࡴ࠰ࠣࡤࡵ࡯ࡰࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡶࡩࡱ࡫࡮ࡪࡷࡰࡤࠬਬ")
bstack1lll11ll1_opy_ = bstack1ll1_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵࠢࡤࡲࡩࠦࡰࡺࡶࡨࡷࡹ࠳ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠡࡲࡤࡧࡰࡧࡧࡦࡵ࠱ࠤࡥࡶࡩࡱࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡴࡾࡺࡥࡴࡶࠣࡴࡾࡺࡥࡴࡶ࠰ࡷࡪࡲࡥ࡯࡫ࡸࡱࡥ࠭ਭ")
bstack1llll1ll1_opy_ = bstack1ll1_opy_ (u"ࠩࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡶࡴࡨ࡯ࡵ࠮ࠣࡴࡦࡨ࡯ࡵࠢࡤࡲࡩࠦࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࡭࡫ࡥࡶࡦࡸࡹࠡࡲࡤࡧࡰࡧࡧࡦࡵࠣࡸࡴࠦࡲࡶࡰࠣࡶࡴࡨ࡯ࡵࠢࡷࡩࡸࡺࡳࠡ࡫ࡱࠤࡵࡧࡲࡢ࡮࡯ࡩࡱ࠴ࠠࡡࡲ࡬ࡴࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡲࡰࡤࡲࡸ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠠࡳࡱࡥࡳࡹ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠮ࡲࡤࡦࡴࡺࠠࡳࡱࡥࡳࡹ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠮ࡵࡨࡰࡪࡴࡩࡶ࡯࡯࡭ࡧࡸࡡࡳࡻࡣࠫਮ")
bstack1l111ll_opy_ = bstack1ll1_opy_ (u"ࠪࡔࡱ࡫ࡡࡴࡧࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡧ࡫ࡨࡢࡸࡨࠤࡹࡵࠠࡳࡷࡱࠤࡹ࡫ࡳࡵࡵ࠱ࠤࡥࡶࡩࡱࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡦࡪ࡮ࡡࡷࡧࡣࠫਯ")
bstack1l11lll1l_opy_ = bstack1ll1_opy_ (u"ࠫࡕࡲࡥࡢࡵࡨࠤ࡮ࡴࡳࡵࡣ࡯ࡰࠥࡧࡰࡱ࡫ࡸࡱ࠲ࡩ࡬ࡪࡧࡱࡸࠥࡺ࡯ࠡࡴࡸࡲࠥࡺࡥࡴࡶࡶ࠲ࠥࡦࡰࡪࡲࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡆࡶࡰࡪࡷࡰ࠱ࡕࡿࡴࡩࡱࡱ࠱ࡈࡲࡩࡦࡰࡷࡤࠬਰ")
bstack1llll111l_opy_ = bstack1ll1_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡸࡴࠦࡲࡶࡰࠣࡸࡪࡹࡴࡴ࠰ࠣࡤࡵ࡯ࡰࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡦࠧ਱")
bstack1l11l11l_opy_ = bstack1ll1_opy_ (u"࠭ࡈࡢࡰࡧࡰ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡦࡰࡴࡹࡥࠨਲ")
bstack1l11lllll_opy_ = bstack1ll1_opy_ (u"ࠧࡂ࡮࡯ࠤࡩࡵ࡮ࡦࠣࠪਲ਼")
bstack1lllll_opy_ = bstack1ll1_opy_ (u"ࠨࡅࡲࡲ࡫࡯ࡧࠡࡨ࡬ࡰࡪࠦࡤࡰࡧࡶࠤࡳࡵࡴࠡࡧࡻ࡭ࡸࡺࠠࡢࡶࠣࡥࡳࡿࠠࡱࡣࡵࡩࡳࡺࠠࡥ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡳ࡫ࠦࠢࡼࡿࠥ࠲ࠥࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡤ࡮ࡸࡨࡪࠦࡡࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺ࡯࡯࠳ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡽࡦࡳ࡬ࠡࡨ࡬ࡰࡪࠦࡣࡰࡰࡷࡥ࡮ࡴࡩ࡯ࡩࠣࡧࡴࡴࡦࡪࡩࡸࡶࡦࡺࡩࡰࡰࠣࡪࡴࡸࠠࡵࡧࡶࡸࡸ࠴ࠧ਴")
bstack11l1llll_opy_ = bstack1ll1_opy_ (u"ࠩࡅࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡥࡵࡩࡩ࡫࡮ࡵ࡫ࡤࡰࡸࠦ࡮ࡰࡶࠣࡴࡷࡵࡶࡪࡦࡨࡨ࠳ࠦࡐ࡭ࡧࡤࡷࡪࠦࡡࡥࡦࠣࡸ࡭࡫࡭ࠡ࡫ࡱࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡽࡲࡲࠠࡤࡱࡱࡪ࡮࡭ࠠࡧ࡫࡯ࡩࠥࡧࡳࠡࠤࡸࡷࡪࡸࡎࡢ࡯ࡨࠦࠥࡧ࡮ࡥࠢࠥࡥࡨࡩࡥࡴࡵࡎࡩࡾࠨࠠࡰࡴࠣࡷࡪࡺࠠࡵࡪࡨࡱࠥࡧࡳࠡࡧࡱࡺ࡮ࡸ࡯࡯࡯ࡨࡲࡹࠦࡶࡢࡴ࡬ࡥࡧࡲࡥࡴ࠼ࠣࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢ࡙ࡘࡋࡒࡏࡃࡐࡉࠧࠦࡡ࡯ࡦࠣࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅࡈࡉࡅࡔࡕࡢࡏࡊ࡟ࠢࠨਵ")
bstack1ll11ll11_opy_ = bstack1ll1_opy_ (u"ࠪࡑࡦࡲࡦࡰࡴࡰࡩࡩࠦࡣࡰࡰࡩ࡭࡬ࠦࡦࡪ࡮ࡨ࠾ࠧࢁࡽࠣࠩਸ਼")
bstack111ll11_opy_ = bstack1ll1_opy_ (u"ࠫࡊࡴࡣࡰࡷࡱࡸࡪࡸࡥࡥࠢࡨࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡷࡳࠤ࠲ࠦࡻࡾࠩ਷")
bstack1l111l1_opy_ = bstack1ll1_opy_ (u"࡙ࠬࡴࡢࡴࡷ࡭ࡳ࡭ࠠࡃࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡌࡰࡥࡤࡰࠬਸ")
bstack1l11l111_opy_ = bstack1ll1_opy_ (u"࠭ࡓࡵࡱࡳࡴ࡮ࡴࡧࠡࡄࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡍࡱࡦࡥࡱ࠭ਹ")
bstack1ll11ll1_opy_ = bstack1ll1_opy_ (u"ࠧࡃࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡌࡰࡥࡤࡰࠥ࡯ࡳࠡࡰࡲࡻࠥࡸࡵ࡯ࡰ࡬ࡲ࡬ࠧࠧ਺")
bstack1llll1ll_opy_ = bstack1ll1_opy_ (u"ࠨࡅࡲࡹࡱࡪࠠ࡯ࡱࡷࠤࡸࡺࡡࡳࡶࠣࡆࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡏࡳࡨࡧ࡬࠻ࠢࡾࢁࠬ਻")
bstack11l1ll1l_opy_ = bstack1ll1_opy_ (u"ࠩࡖࡸࡦࡸࡴࡪࡰࡪࠤࡱࡵࡣࡢ࡮ࠣࡦ࡮ࡴࡡࡳࡻࠣࡻ࡮ࡺࡨࠡࡱࡳࡸ࡮ࡵ࡮ࡴ࠼ࠣࡿࢂ਼࠭")
bstack1ll1lll11_opy_ = bstack1ll1_opy_ (u"࡙ࠪࡵࡪࡡࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡤࡦࡶࡤ࡭ࡱࡹ࠺ࠡࡽࢀࠫ਽")
bstack1l1l1ll_opy_ = bstack1ll1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡳࡦࡶࡷ࡭ࡳ࡭ࠠࡶࡲࡧࡥࡹ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡴࡶࡤࡸࡺࡹࠠࡼࡿࠪਾ")
bstack1111l1l1_opy_ = bstack1ll1_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥࡶࡲࡰࡸ࡬ࡨࡪࠦࡡ࡯ࠢࡤࡴࡵࡸ࡯ࡱࡴ࡬ࡥࡹ࡫ࠠࡇ࡙ࠣࠬࡷࡵࡢࡰࡶ࠲ࡴࡦࡨ࡯ࡵࠫࠣ࡭ࡳࠦࡣࡰࡰࡩ࡭࡬ࠦࡦࡪ࡮ࡨ࠰ࠥࡹ࡫ࡪࡲࠣࡸ࡭࡫ࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠣ࡯ࡪࡿࠠࡪࡰࠣࡧࡴࡴࡦࡪࡩࠣ࡭࡫ࠦࡲࡶࡰࡱ࡭ࡳ࡭ࠠࡴ࡫ࡰࡴࡱ࡫ࠠࡱࡻࡷ࡬ࡴࡴࠠࡴࡥࡵ࡭ࡵࡺࠠࡸ࡫ࡷ࡬ࡴࡻࡴࠡࡣࡱࡽࠥࡌࡗ࠯ࠩਿ")
bstack11lllll_opy_ = bstack1ll1_opy_ (u"࠭ࡓࡦࡶࡷ࡭ࡳ࡭ࠠࡩࡶࡷࡴࡕࡸ࡯ࡹࡻ࠲࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠠࡪࡵࠣࡲࡴࡺࠠࡴࡷࡳࡴࡴࡸࡴࡦࡦࠣࡳࡳࠦࡣࡶࡴࡵࡩࡳࡺ࡬ࡺࠢ࡬ࡲࡸࡺࡡ࡭࡮ࡨࡨࠥࡼࡥࡳࡵ࡬ࡳࡳࠦ࡯ࡧࠢࡶࡩࡱ࡫࡮ࡪࡷࡰࠤ࠭ࢁࡽࠪ࠮ࠣࡴࡱ࡫ࡡࡴࡧࠣࡹࡵ࡭ࡲࡢࡦࡨࠤࡹࡵࠠࡔࡧ࡯ࡩࡳ࡯ࡵ࡮ࡀࡀ࠸࠳࠶࠮࠱ࠢࡲࡶࠥࡸࡥࡧࡧࡵࠤࡹࡵࠠࡩࡶࡷࡴࡸࡀ࠯࠰ࡹࡺࡻ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡦࡲࡧࡸ࠵ࡡࡶࡶࡲࡱࡦࡺࡥ࠰ࡵࡨࡰࡪࡴࡩࡶ࡯࠲ࡶࡺࡴ࠭ࡵࡧࡶࡸࡸ࠳ࡢࡦࡪ࡬ࡲࡩ࠳ࡰࡳࡱࡻࡽࠨࡶࡹࡵࡪࡲࡲࠥ࡬࡯ࡳࠢࡤࠤࡼࡵࡲ࡬ࡣࡵࡳࡺࡴࡤ࠯ࠩੀ")
bstack1111llll_opy_ = bstack1ll1_opy_ (u"ࠧࡈࡧࡱࡩࡷࡧࡴࡪࡰࡪࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡧࡴࡴࡦࡪࡩࡸࡶࡦࡺࡩࡰࡰࠣࡽࡲࡲࠠࡧ࡫࡯ࡩ࠳࠴ࠧੁ")
bstack11111ll_opy_ = bstack1ll1_opy_ (u"ࠨࡕࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡨࡧࡱࡩࡷࡧࡴࡦࡦࠣࡸ࡭࡫ࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠࡧ࡫࡯ࡩࠦ࠭ੂ")
bstack1l111111_opy_ = bstack1ll1_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥ࡯ࡧࡵࡥࡹ࡫ࠠࡵࡪࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡧࡴࡴࡦࡪࡩࡸࡶࡦࡺࡩࡰࡰࠣࡪ࡮ࡲࡥ࠯ࠢࡾࢁࠬ੃")
bstack1lll1lll_opy_ = bstack1ll1_opy_ (u"ࠪࡉࡽࡶࡥࡤࡶࡨࡨࠥࡧࡴࠡ࡮ࡨࡥࡸࡺࠠ࠲ࠢ࡬ࡲࡵࡻࡴ࠭ࠢࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࠵࠭੄")
bstack111llll1_opy_ = bstack1ll1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡨࡺࡸࡩ࡯ࡩࠣࡅࡵࡶࠠࡶࡲ࡯ࡳࡦࡪ࠮ࠡࡽࢀࠫ੅")
bstack111ll11l_opy_ = bstack1ll1_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡷࡳࡰࡴࡧࡤࠡࡃࡳࡴ࠳ࠦࡉ࡯ࡸࡤࡰ࡮ࡪࠠࡧ࡫࡯ࡩࠥࡶࡡࡵࡪࠣࡴࡷࡵࡶࡪࡦࡨࡨࠥࢁࡽ࠯ࠩ੆")
bstack1ll11ll_opy_ = bstack1ll1_opy_ (u"࠭ࡋࡦࡻࡶࠤࡨࡧ࡮࡯ࡱࡷࠤࡨࡵ࠭ࡦࡺ࡬ࡷࡹࠦࡡࡴࠢࡤࡴࡵࠦࡶࡢ࡮ࡸࡩࡸ࠲ࠠࡶࡵࡨࠤࡦࡴࡹࠡࡱࡱࡩࠥࡶࡲࡰࡲࡨࡶࡹࡿࠠࡧࡴࡲࡱࠥࢁࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀ࠯ࠤࡵࡧࡴࡩ࠾ࡶࡸࡷ࡯࡮ࡨࡀ࠯ࠤࡨࡻࡳࡵࡱࡰࡣ࡮ࡪ࠼ࡴࡶࡵ࡭ࡳ࡭࠾࠭ࠢࡶ࡬ࡦࡸࡥࡢࡤ࡯ࡩࡤ࡯ࡤ࠽ࡵࡷࡶ࡮ࡴࡧ࠿ࡿ࠯ࠤࡴࡴ࡬ࡺࠢࠥࡴࡦࡺࡨࠣࠢࡤࡲࡩࠦࠢࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠥࠤࡨࡧ࡮ࠡࡥࡲ࠱ࡪࡾࡩࡴࡶࠣࡸࡴ࡭ࡥࡵࡪࡨࡶ࠳࠭ੇ")
bstack1l1ll1l1l_opy_ = bstack1ll1_opy_ (u"ࠧ࡜ࡋࡱࡺࡦࡲࡩࡥࠢࡤࡴࡵࠦࡰࡳࡱࡳࡩࡷࡺࡹ࡞ࠢࡶࡹࡵࡶ࡯ࡳࡶࡨࡨࠥࡶࡲࡰࡲࡨࡶࡹ࡯ࡥࡴࠢࡤࡶࡪࠦࡻࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁ࠰ࠥࡶࡡࡵࡪ࠿ࡷࡹࡸࡩ࡯ࡩࡁ࠰ࠥࡩࡵࡴࡶࡲࡱࡤ࡯ࡤ࠽ࡵࡷࡶ࡮ࡴࡧ࠿࠮ࠣࡷ࡭ࡧࡲࡦࡣࡥࡰࡪࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀࢀ࠲ࠥࡌ࡯ࡳࠢࡰࡳࡷ࡫ࠠࡥࡧࡷࡥ࡮ࡲࡳࠡࡲ࡯ࡩࡦࡹࡥࠡࡸ࡬ࡷ࡮ࡺࠠࡩࡶࡷࡴࡸࡀ࠯࠰ࡹࡺࡻ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡦࡲࡧࡸ࠵ࡡࡱࡲ࠰ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠴ࡧࡰࡱ࡫ࡸࡱ࠴ࡹࡥࡵ࠯ࡸࡴ࠲ࡺࡥࡴࡶࡶ࠳ࡸࡶࡥࡤ࡫ࡩࡽ࠲ࡧࡰࡱࠩੈ")
bstack111ll1l1_opy_ = bstack1ll1_opy_ (u"ࠨ࡝ࡌࡲࡻࡧ࡬ࡪࡦࠣࡥࡵࡶࠠࡱࡴࡲࡴࡪࡸࡴࡺ࡟ࠣࡗࡺࡶࡰࡰࡴࡷࡩࡩࠦࡶࡢ࡮ࡸࡩࡸࠦ࡯ࡧࠢࡤࡴࡵࠦࡡࡳࡧࠣࡳ࡫ࠦࡻࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁ࠰ࠥࡶࡡࡵࡪ࠿ࡷࡹࡸࡩ࡯ࡩࡁ࠰ࠥࡩࡵࡴࡶࡲࡱࡤ࡯ࡤ࠽ࡵࡷࡶ࡮ࡴࡧ࠿࠮ࠣࡷ࡭ࡧࡲࡦࡣࡥࡰࡪࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀࢀ࠲ࠥࡌ࡯ࡳࠢࡰࡳࡷ࡫ࠠࡥࡧࡷࡥ࡮ࡲࡳࠡࡲ࡯ࡩࡦࡹࡥࠡࡸ࡬ࡷ࡮ࡺࠠࡩࡶࡷࡴࡸࡀ࠯࠰ࡹࡺࡻ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡦࡲࡧࡸ࠵ࡡࡱࡲ࠰ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠴ࡧࡰࡱ࡫ࡸࡱ࠴ࡹࡥࡵ࠯ࡸࡴ࠲ࡺࡥࡴࡶࡶ࠳ࡸࡶࡥࡤ࡫ࡩࡽ࠲ࡧࡰࡱࠩ੉")
bstack1llllll1l_opy_ = bstack1ll1_opy_ (u"ࠩࡘࡷ࡮ࡴࡧࠡࡧࡻ࡭ࡸࡺࡩ࡯ࡩࠣࡥࡵࡶࠠࡪࡦࠣࡿࢂࠦࡦࡰࡴࠣ࡬ࡦࡹࡨࠡ࠼ࠣࡿࢂ࠴ࠧ੊")
bstack11lllll1_opy_ = bstack1ll1_opy_ (u"ࠪࡅࡵࡶࠠࡖࡲ࡯ࡳࡦࡪࡥࡥࠢࡖࡹࡨࡩࡥࡴࡵࡩࡹࡱࡲࡹ࠯ࠢࡌࡈࠥࡀࠠࡼࡿࠪੋ")
bstack1l11l11_opy_ = bstack1ll1_opy_ (u"࡚ࠫࡹࡩ࡯ࡩࠣࡅࡵࡶࠠ࠻ࠢࡾࢁ࠳࠭ੌ")
bstack11ll1l_opy_ = bstack1ll1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠥ࡯ࡳࠡࡰࡲࡸࠥࡹࡵࡱࡲࡲࡶࡹ࡫ࡤࠡࡨࡲࡶࠥࡼࡡ࡯࡫࡯ࡰࡦࠦࡰࡺࡶ࡫ࡳࡳࠦࡴࡦࡵࡷࡷ࠱ࠦࡲࡶࡰࡱ࡭ࡳ࡭ࠠࡸ࡫ࡷ࡬ࠥࡶࡡࡳࡣ࡯ࡰࡪࡲࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠤࡂࠦ࠱ࠨ੍")
bstack11111l_opy_ = bstack1ll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡥࡵࡩࡦࡺࡩ࡯ࡩࠣࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶ࠿ࠦࡻࡾࠩ੎")
bstack1l11llll1_opy_ = bstack1ll1_opy_ (u"ࠧࡄࡱࡸࡰࡩࠦ࡮ࡰࡶࠣࡧࡱࡵࡳࡦࠢࡥࡶࡴࡽࡳࡦࡴ࠽ࠤࢀࢃࠧ੏")
bstack1l1l1ll1l_opy_ = bstack1ll1_opy_ (u"ࠨࡅࡲࡹࡱࡪࠠ࡯ࡱࡷࠤ࡬࡫ࡴࠡࡴࡨࡥࡸࡵ࡮ࠡࡨࡲࡶࠥࡨࡥࡩࡣࡹࡩࠥ࡬ࡥࡢࡶࡸࡶࡪࠦࡦࡢ࡫࡯ࡹࡷ࡫࠮ࠡࡽࢀࠫ੐")
bstack11ll1l1_opy_ = bstack1ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡴࡨࡷࡵࡵ࡮ࡴࡧࠣࡪࡷࡵ࡭ࠡࡣࡳ࡭ࠥࡩࡡ࡭࡮࠱ࠤࡊࡸࡲࡰࡴ࠽ࠤࢀࢃࠧੑ")
bstack11ll1ll_opy_ = bstack1ll1_opy_ (u"࡙ࠪࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡩࡱࡺࠤࡧࡻࡩ࡭ࡦ࡙ࠣࡗࡒࠬࠡࡣࡶࠤࡧࡻࡩ࡭ࡦࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹࡿࠠࡪࡵࠣࡲࡴࡺࠠࡶࡵࡨࡨ࠳࠭੒")
bstack1111_opy_ = bstack1ll1_opy_ (u"ࠫࡘ࡫ࡲࡷࡧࡵࠤࡸ࡯ࡤࡦࠢࡥࡹ࡮ࡲࡤࡏࡣࡰࡩ࠭ࢁࡽࠪࠢ࡬ࡷࠥࡴ࡯ࡵࠢࡶࡥࡲ࡫ࠠࡢࡵࠣࡧࡱ࡯ࡥ࡯ࡶࠣࡷ࡮ࡪࡥࠡࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠬࢀࢃࠩࠨ੓")
bstack1lll11_opy_ = bstack1ll1_opy_ (u"ࠬ࡜ࡩࡦࡹࠣࡦࡺ࡯࡬ࡥࠢࡲࡲࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡩࡧࡳࡩࡤࡲࡥࡷࡪ࠺ࠡࡽࢀࠫ੔")
bstack1111111l_opy_ = bstack1ll1_opy_ (u"࠭ࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡤࡧࡨ࡫ࡳࡴࠢࡤࠤࡵࡸࡩࡷࡣࡷࡩࠥࡪ࡯࡮ࡣ࡬ࡲ࠿ࠦࡻࡾࠢ࠱ࠤࡘ࡫ࡴࠡࡶ࡫ࡩࠥ࡬࡯࡭࡮ࡲࡻ࡮ࡴࡧࠡࡥࡲࡲ࡫࡯ࡧࠡ࡫ࡱࠤࡾࡵࡵࡳࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰࠥ࡬ࡩ࡭ࡧ࠽ࠤࡡࡴ࠭࠮࠯࠰࠱࠲࠳࠭࠮࠯࠰ࠤࡡࡴࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯࠾ࠥࡺࡲࡶࡧࠣࡠࡳ࠳࠭࠮࠯࠰࠱࠲࠳࠭࠮࠯ࠪ੕")
bstack1l1l1ll1_opy_ = bstack1ll1_opy_ (u"ࠧࡔࡱࡰࡩࡹ࡮ࡩ࡯ࡩࠣࡻࡪࡴࡴࠡࡹࡵࡳࡳ࡭ࠠࡸࡪ࡬ࡰࡪࠦࡥࡹࡧࡦࡹࡹ࡯࡮ࡨࠢࡪࡩࡹࡥ࡮ࡶࡦࡪࡩࡤࡲ࡯ࡤࡣ࡯ࡣࡪࡸࡲࡰࡴࠣ࠾ࠥࢁࡽࠨ੖")
bstack11ll11l_opy_ = bstack1ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡪࡰࠣࡷࡪࡴࡤࡠࡣࡰࡴࡱ࡯ࡴࡶࡦࡨࡣࡪࡼࡥ࡯ࡶࠣࡪࡴࡸࠠࡔࡆࡎࡗࡪࡺࡵࡱࠢࡾࢁࠧ੗")
bstack1l1l1lll_opy_ = bstack1ll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫࡮ࡥࡡࡤࡱࡵࡲࡩࡵࡷࡧࡩࡤ࡫ࡶࡦࡰࡷࠤ࡫ࡵࡲࠡࡕࡇࡏ࡙࡫ࡳࡵࡃࡷࡸࡪࡳࡰࡵࡧࡧࠤࢀࢃࠢ੘")
bstack1l1lll11l_opy_ = bstack1ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥ࡯ࡦࡢࡥࡲࡶ࡬ࡪࡶࡸࡨࡪࡥࡥࡷࡧࡱࡸࠥ࡬࡯ࡳࠢࡖࡈࡐ࡚ࡥࡴࡶࡖࡹࡨࡩࡥࡴࡵࡩࡹࡱࠦࡻࡾࠤਖ਼")
bstack1l1l11111_opy_ = bstack1ll1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡦࡪࡴࡨࡣࡷ࡫ࡱࡶࡧࡶࡸࠥࢁࡽࠣਗ਼")
bstack11ll11_opy_ = bstack1ll1_opy_ (u"ࠧࡖࡏࡔࡖࠣࡉࡻ࡫࡮ࡵࠢࡾࢁࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠠ࠻ࠢࡾࢁࠧਜ਼")
bstack1l11ll1ll_opy_ = bstack1ll1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡩࠥࡶࡲࡰࡺࡼࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࡸ࠲ࠠࡦࡴࡵࡳࡷࡀࠠࡼࡿࠪੜ")
bstack11l111l1_opy_ = bstack1ll1_opy_ (u"ࠧࠡࠢ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠠࠡ࡫ࡩࠬࡵࡧࡧࡦࠢࡀࡁࡂࠦࡶࡰ࡫ࡧࠤ࠵࠯ࠠࡼ࡞ࡱࠤࠥࠦࡴࡳࡻࡾࡠࡳࠦࡣࡰࡰࡶࡸࠥ࡬ࡳࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࡡ࠭ࡦࡴ࡞ࠪ࠭ࡀࡢ࡮ࠡࠢࠣࠤࠥ࡬ࡳ࠯ࡣࡳࡴࡪࡴࡤࡇ࡫࡯ࡩࡘࡿ࡮ࡤࠪࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠬࠡࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡳࡣ࡮ࡴࡤࡦࡺࠬࠤ࠰ࠦࠢ࠻ࠤࠣ࠯ࠥࡐࡓࡐࡐ࠱ࡷࡹࡸࡩ࡯ࡩ࡬ࡪࡾ࠮ࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࠬࡦࡽࡡࡪࡶࠣࡲࡪࡽࡐࡢࡩࡨ࠶࠳࡫ࡶࡢ࡮ࡸࡥࡹ࡫ࠨࠣࠪࠬࠤࡂࡄࠠࡼࡿࠥ࠰ࠥࡢࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡨࡧࡷࡗࡪࡹࡳࡪࡱࡱࡈࡪࡺࡡࡪ࡮ࡶࠦࢂࡢࠧࠪࠫࠬ࡟ࠧ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠣ࡟ࠬࠤ࠰ࠦࠢ࠭࡞࡟ࡲࠧ࠯࡜࡯ࠢࠣࠤࠥࢃࡣࡢࡶࡦ࡬࠭࡫ࡸࠪࡽ࡟ࡲࠥࠦࠠࠡࡿ࡟ࡲࠥࠦࡽ࡝ࡰࠣࠤ࠴࠰ࠠ࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࠤ࠯࠵ࠧ੝")
bstack1ll1llll1_opy_ = bstack1ll1_opy_ (u"ࠨ࡞ࡱ࠳࠯ࠦ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࠣ࠮࠴ࡢ࡮ࡤࡱࡱࡷࡹࠦࡢࡴࡶࡤࡧࡰࡥࡰࡢࡶ࡫ࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࡠࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠳࡞࡞ࡱࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡦࡥࡵࡹࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠴ࡡࡡࡴࡣࡰࡰࡶࡸࠥࡶ࡟ࡪࡰࡧࡩࡽࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࡛ࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠴ࡠࡠࡳࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡹ࡬ࡪࡥࡨࠬ࠵࠲ࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠵ࠬࡠࡳࡩ࡯࡯ࡵࡷࠤ࡮ࡳࡰࡰࡴࡷࡣࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴ࠵ࡡࡥࡷࡹࡧࡣ࡬ࠢࡀࠤࡷ࡫ࡱࡶ࡫ࡵࡩ࠭ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥ࠭ࡀࡢ࡮ࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮࡭ࡣࡸࡲࡨ࡮ࠠ࠾ࠢࡤࡷࡾࡴࡣࠡࠪ࡯ࡥࡺࡴࡣࡩࡑࡳࡸ࡮ࡵ࡮ࡴࠫࠣࡁࡃࠦࡻ࡝ࡰ࡯ࡩࡹࠦࡣࡢࡲࡶ࠿ࡡࡴࡴࡳࡻࠣࡿࡡࡴࡣࡢࡲࡶࠤࡂࠦࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࡦࡸࡺࡡࡤ࡭ࡢࡧࡦࡶࡳࠪ࡞ࡱࠤࠥࢃࠠࡤࡣࡷࡧ࡭࠮ࡥࡹࠫࠣࡿࡡࡴࠠࠡࠢࠣࢁࡡࡴࠠࠡࡴࡨࡸࡺࡸ࡮ࠡࡣࡺࡥ࡮ࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮ࡤࡱࡱࡲࡪࡩࡴࠩࡽ࡟ࡲࠥࠦࠠࠡࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸ࠿ࠦࡠࡸࡵࡶ࠾࠴࠵ࡣࡥࡲ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡂࡧࡦࡶࡳ࠾ࠦࡾࡩࡳࡩ࡯ࡥࡧࡘࡖࡎࡉ࡯࡮ࡲࡲࡲࡪࡴࡴࠩࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡦࡥࡵࡹࠩࠪࡿࡣ࠰ࡡࡴࠠࠡࠢࠣ࠲࠳࠴࡬ࡢࡷࡱࡧ࡭ࡕࡰࡵ࡫ࡲࡲࡸࡢ࡮ࠡࠢࢀ࠭ࡡࡴࡽ࡝ࡰ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠧਫ਼")
from ._version import __version__
bstack11llll11_opy_ = None
CONFIG = {}
bstack1111l1l_opy_ = {}
bstack1lll1111l_opy_ = {}
bstack1111111_opy_ = None
bstack111lll_opy_ = None
bstack1ll111ll_opy_ = None
bstack1111ll_opy_ = -1
bstack1ll1lll1_opy_ = DEFAULT_LOG_LEVEL
bstack1llll1_opy_ = 1
bstack1l1ll1l_opy_ = False
bstack1l1l1l11_opy_ = bstack1ll1_opy_ (u"ࠩࠪ੟")
bstack111l1lll_opy_ = bstack1ll1_opy_ (u"ࠪࠫ੠")
bstack1ll11111l_opy_ = False
bstack111lllll_opy_ = True
bstack11l1l11l_opy_ = bstack1ll1_opy_ (u"ࠫࠬ੡")
bstack111l_opy_ = []
bstack1lll1_opy_ = None
bstack1ll1l11l_opy_ = None
bstack1111l11l_opy_ = None
bstack11l11ll1_opy_ = None
bstack1ll111_opy_ = None
bstack1111l1ll_opy_ = None
bstack1ll11111_opy_ = None
bstack111lll1l_opy_ = None
bstack1ll1l1ll1_opy_ = None
bstack1l1lll_opy_ = None
bstack1lll1l_opy_ = None
bstack11ll1l1l_opy_ = None
bstack1l1ll_opy_ = bstack1ll1_opy_ (u"ࠧࠨ੢")
class bstack11lll1ll_opy_(threading.Thread):
  def run(self):
    self.exc = None
    try:
      self.ret = self._target(*self._args, **self._kwargs)
    except Exception as e:
      self.exc = e
  def join(self, timeout=None):
    super(bstack11lll1ll_opy_, self).join(timeout)
    if self.exc:
      raise self.exc
    return self.ret
logger = logging.getLogger(__name__)
logging.basicConfig(level=bstack1ll1lll1_opy_,
                    format=bstack1ll1_opy_ (u"࠭࡜࡯ࠧࠫࡥࡸࡩࡴࡪ࡯ࡨ࠭ࡸ࡛ࠦࠦࠪࡱࡥࡲ࡫ࠩࡴ࡟࡞ࠩ࠭ࡲࡥࡷࡧ࡯ࡲࡦࡳࡥࠪࡵࡠࠤ࠲ࠦࠥࠩ࡯ࡨࡷࡸࡧࡧࡦࠫࡶࠫ੣"),
                    datefmt=bstack1ll1_opy_ (u"ࠧࠦࡊ࠽ࠩࡒࡀࠥࡔࠩ੤"))
def bstack11l111ll_opy_():
  global CONFIG
  global bstack1ll1lll1_opy_
  if bstack1ll1_opy_ (u"ࠨ࡮ࡲ࡫ࡑ࡫ࡶࡦ࡮ࠪ੥") in CONFIG:
    bstack1ll1lll1_opy_ = bstack1ll1l1_opy_[CONFIG[bstack1ll1_opy_ (u"ࠩ࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫ੦")]]
    logging.getLogger().setLevel(bstack1ll1lll1_opy_)
def bstack1lllll1_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1ll1llll_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll1ll111_opy_():
  args = sys.argv
  for i in range(len(args)):
    if bstack1ll1_opy_ (u"ࠥ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡧࡴࡴࡦࡪࡩࡩ࡭ࡱ࡫ࠢ੧") == args[i].lower() or bstack1ll1_opy_ (u"ࠦ࠲࠳ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡯ࡨ࡬࡫ࠧ੨") == args[i].lower():
      path = args[i+1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      global bstack11l1l11l_opy_
      bstack11l1l11l_opy_ += bstack1ll1_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡉ࡯࡯ࡨ࡬࡫ࡋ࡯࡬ࡦࠢࠪ੩") + path
      return path
  return None
def bstack1l1ll1ll_opy_():
  bstack111llll_opy_ = bstack1ll1ll111_opy_()
  if bstack111llll_opy_ and os.path.exists(os.path.abspath(bstack111llll_opy_)):
    fileName = bstack111llll_opy_
  if bstack1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡉࡏࡏࡈࡌࡋࡤࡌࡉࡍࡇࠪ੪") in os.environ and os.path.exists(os.path.abspath(os.environ[bstack1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌࡥࡆࡊࡎࡈࠫ੫")])) and not bstack1ll1_opy_ (u"ࠨࡨ࡬ࡰࡪࡔࡡ࡮ࡧࠪ੬") in locals():
    fileName = os.environ[bstack1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡒࡒࡋࡏࡇࡠࡈࡌࡐࡊ࠭੭")]
  if bstack1ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡏࡣࡰࡩࠬ੮") in locals():
    bstack1l11_opy_ = os.path.abspath(fileName)
  else:
    bstack1l11_opy_ = bstack1ll1_opy_ (u"ࠫࠬ੯")
  bstack1ll1l1l11_opy_ = os.getcwd()
  bstack1ll11l1_opy_ = bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠨੰ")
  bstack1l1l111_opy_ = bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿࡡ࡮࡮ࠪੱ")
  while (not os.path.exists(bstack1l11_opy_)) and bstack1ll1l1l11_opy_ != bstack1ll1_opy_ (u"ࠢࠣੲ"):
    bstack1l11_opy_ = os.path.join(bstack1ll1l1l11_opy_, bstack1ll11l1_opy_)
    if not os.path.exists(bstack1l11_opy_):
      bstack1l11_opy_ = os.path.join(bstack1ll1l1l11_opy_, bstack1l1l111_opy_)
    if bstack1ll1l1l11_opy_ != os.path.dirname(bstack1ll1l1l11_opy_):
      bstack1ll1l1l11_opy_ = os.path.dirname(bstack1ll1l1l11_opy_)
    else:
      bstack1ll1l1l11_opy_ = bstack1ll1_opy_ (u"ࠣࠤੳ")
  if not os.path.exists(bstack1l11_opy_):
    bstack1ll1lll_opy_(
      bstack1lllll_opy_.format(os.getcwd()))
  with open(bstack1l11_opy_, bstack1ll1_opy_ (u"ࠩࡵࠫੴ")) as stream:
    try:
      config = yaml.safe_load(stream)
      return config
    except yaml.YAMLError as exc:
      bstack1ll1lll_opy_(bstack1ll11ll11_opy_.format(str(exc)))
def bstack11ll1lll_opy_(config):
  bstack1ll1ll1_opy_ = bstack1ll11l11l_opy_(config)
  for option in list(bstack1ll1ll1_opy_):
    if option.lower() in bstack1ll111l1l_opy_ and option != bstack1ll111l1l_opy_[option.lower()]:
      bstack1ll1ll1_opy_[bstack1ll111l1l_opy_[option.lower()]] = bstack1ll1ll1_opy_[option]
      del bstack1ll1ll1_opy_[option]
  return config
def bstack1lll1ll1_opy_():
  global bstack1lll1111l_opy_
  for key, bstack1111lll1_opy_ in bstack1l111l_opy_.items():
    if isinstance(bstack1111lll1_opy_, list):
      for var in bstack1111lll1_opy_:
        if var in os.environ:
          bstack1lll1111l_opy_[key] = os.environ[var]
          break
    elif bstack1111lll1_opy_ in os.environ:
      bstack1lll1111l_opy_[key] = os.environ[bstack1111lll1_opy_]
  if bstack1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡏࡓࡈࡇࡌࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠬੵ") in os.environ:
    bstack1lll1111l_opy_[bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨ੶")] = {}
    bstack1lll1111l_opy_[bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ੷")][bstack1ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ੸")] = os.environ[bstack1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ੹")]
def bstack1l11l_opy_():
  global bstack1111l1l_opy_
  global bstack11l1l11l_opy_
  for idx, val in enumerate(sys.argv):
    if idx<len(sys.argv) and bstack1ll1_opy_ (u"ࠨ࠯࠰ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ੺").lower() == val.lower():
      bstack1111l1l_opy_[bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭੻")] = {}
      bstack1111l1l_opy_[bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ੼")][bstack1ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭੽")] = sys.argv[idx+1]
      del sys.argv[idx:idx+2]
      break
  for key, bstack1lll111l_opy_ in bstack11l11lll_opy_.items():
    if isinstance(bstack1lll111l_opy_, list):
      for idx, val in enumerate(sys.argv):
        for var in bstack1lll111l_opy_:
          if idx<len(sys.argv) and bstack1ll1_opy_ (u"ࠬ࠳࠭ࠨ੾") + var.lower() == val.lower() and not key in bstack1111l1l_opy_:
            bstack1111l1l_opy_[key] = sys.argv[idx+1]
            bstack11l1l11l_opy_ += bstack1ll1_opy_ (u"࠭ࠠ࠮࠯ࠪ੿") + var + bstack1ll1_opy_ (u"ࠧࠡࠩ઀") + sys.argv[idx+1]
            del sys.argv[idx:idx+2]
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx<len(sys.argv) and bstack1ll1_opy_ (u"ࠨ࠯࠰ࠫઁ") + bstack1lll111l_opy_.lower() == val.lower() and not key in bstack1111l1l_opy_:
          bstack1111l1l_opy_[key] = sys.argv[idx+1]
          bstack11l1l11l_opy_ += bstack1ll1_opy_ (u"ࠩࠣ࠱࠲࠭ં") + bstack1lll111l_opy_ + bstack1ll1_opy_ (u"ࠪࠤࠬઃ") + sys.argv[idx+1]
          del sys.argv[idx:idx+2]
def bstack1ll11lll_opy_(config):
  bstack1l11111_opy_ = config.keys()
  for bstack11l1111l_opy_, bstack1l1l111ll_opy_ in bstack111l11l_opy_.items():
    if bstack1l1l111ll_opy_ in bstack1l11111_opy_:
      config[bstack11l1111l_opy_] = config[bstack1l1l111ll_opy_]
      del config[bstack1l1l111ll_opy_]
  for bstack11l1111l_opy_, bstack1l1l111ll_opy_ in bstack1l1ll1111_opy_.items():
    if isinstance(bstack1l1l111ll_opy_, list):
      for bstack1lllll1l1_opy_ in bstack1l1l111ll_opy_:
        if bstack1lllll1l1_opy_ in bstack1l11111_opy_:
          config[bstack11l1111l_opy_] = config[bstack1lllll1l1_opy_]
          del config[bstack1lllll1l1_opy_]
          break
    elif bstack1l1l111ll_opy_ in bstack1l11111_opy_:
        config[bstack11l1111l_opy_] = config[bstack1l1l111ll_opy_]
        del config[bstack1l1l111ll_opy_]
  for bstack1lllll1l1_opy_ in list(config):
    for bstack1l1lllll_opy_ in bstack11111l1l_opy_:
      if bstack1lllll1l1_opy_.lower() == bstack1l1lllll_opy_.lower() and bstack1lllll1l1_opy_ != bstack1l1lllll_opy_:
        config[bstack1l1lllll_opy_] = config[bstack1lllll1l1_opy_]
        del config[bstack1lllll1l1_opy_]
  bstack1l1l1l11l_opy_ = []
  if bstack1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ઄") in config:
    bstack1l1l1l11l_opy_ = config[bstack1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨઅ")]
  for platform in bstack1l1l1l11l_opy_:
    for bstack1lllll1l1_opy_ in list(platform):
      for bstack1l1lllll_opy_ in bstack11111l1l_opy_:
        if bstack1lllll1l1_opy_.lower() == bstack1l1lllll_opy_.lower() and bstack1lllll1l1_opy_ != bstack1l1lllll_opy_:
          platform[bstack1l1lllll_opy_] = platform[bstack1lllll1l1_opy_]
          del platform[bstack1lllll1l1_opy_]
  for bstack11l1111l_opy_, bstack1l1l111ll_opy_ in bstack1l1ll1111_opy_.items():
    for platform in bstack1l1l1l11l_opy_:
      if isinstance(bstack1l1l111ll_opy_, list):
        for bstack1lllll1l1_opy_ in bstack1l1l111ll_opy_:
          if bstack1lllll1l1_opy_ in platform:
            platform[bstack11l1111l_opy_] = platform[bstack1lllll1l1_opy_]
            del platform[bstack1lllll1l1_opy_]
            break
      elif bstack1l1l111ll_opy_ in platform:
        platform[bstack11l1111l_opy_] = platform[bstack1l1l111ll_opy_]
        del platform[bstack1l1l111ll_opy_]
  for bstack1lll11lll_opy_ in bstack11l1ll11_opy_:
    if bstack1lll11lll_opy_ in config:
      if not bstack11l1ll11_opy_[bstack1lll11lll_opy_] in config:
        config[bstack11l1ll11_opy_[bstack1lll11lll_opy_]] = {}
      config[bstack11l1ll11_opy_[bstack1lll11lll_opy_]].update(config[bstack1lll11lll_opy_])
      del config[bstack1lll11lll_opy_]
  for platform in bstack1l1l1l11l_opy_:
    for bstack1lll11lll_opy_ in bstack11l1ll11_opy_:
      if bstack1lll11lll_opy_ in list(platform):
        if not bstack11l1ll11_opy_[bstack1lll11lll_opy_] in platform:
          platform[bstack11l1ll11_opy_[bstack1lll11lll_opy_]] = {}
        platform[bstack11l1ll11_opy_[bstack1lll11lll_opy_]].update(platform[bstack1lll11lll_opy_])
        del platform[bstack1lll11lll_opy_]
  config = bstack11ll1lll_opy_(config)
  return config
def bstack1ll111lll_opy_(config):
  global bstack111l1lll_opy_
  if bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪઆ") in config and str(config[bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫઇ")]).lower() != bstack1ll1_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧઈ"):
    if not bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ઉ") in config:
      config[bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧઊ")] = {}
    if not bstack1ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ઋ") in config[bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩઌ")]:
      bstack1lll11l1l_opy_ = datetime.datetime.now()
      bstack1lll11l11_opy_ = bstack1lll11l1l_opy_.strftime(bstack1ll1_opy_ (u"࠭ࠥࡥࡡࠨࡦࡤࠫࡈࠦࡏࠪઍ"))
      hostname = socket.gethostname()
      bstack1ll11_opy_ = bstack1ll1_opy_ (u"ࠧࠨ઎").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack1ll1_opy_ (u"ࠨࡽࢀࡣࢀࢃ࡟ࡼࡿࠪએ").format(bstack1lll11l11_opy_, hostname, bstack1ll11_opy_)
      config[bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ઐ")][bstack1ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬઑ")] = identifier
    bstack111l1lll_opy_ = config[bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨ઒")][bstack1ll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧઓ")]
  return config
def bstack1lll1l11_opy_():
  if (
    isinstance(os.getenv(bstack1ll1_opy_ (u"࠭ࡊࡆࡐࡎࡍࡓ࡙࡟ࡖࡔࡏࠫઔ")), str) and len(os.getenv(bstack1ll1_opy_ (u"ࠧࡋࡇࡑࡏࡎࡔࡓࡠࡗࡕࡐࠬક"))) > 0
  ) or (
    isinstance(os.getenv(bstack1ll1_opy_ (u"ࠨࡌࡈࡒࡐࡏࡎࡔࡡࡋࡓࡒࡋࠧખ")), str) and len(os.getenv(bstack1ll1_opy_ (u"ࠩࡍࡉࡓࡑࡉࡏࡕࡢࡌࡔࡓࡅࠨગ"))) > 0
  ):
    return os.getenv(bstack1ll1_opy_ (u"ࠪࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠩઘ"), 0)
  if str(os.getenv(bstack1ll1_opy_ (u"ࠫࡈࡏࠧઙ"))).lower() == bstack1ll1_opy_ (u"ࠬࡺࡲࡶࡧࠪચ") and str(os.getenv(bstack1ll1_opy_ (u"࠭ࡃࡊࡔࡆࡐࡊࡉࡉࠨછ"))).lower() == bstack1ll1_opy_ (u"ࠧࡵࡴࡸࡩࠬજ"):
    return os.getenv(bstack1ll1_opy_ (u"ࠨࡅࡌࡖࡈࡒࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࠫઝ"), 0)
  if str(os.getenv(bstack1ll1_opy_ (u"ࠩࡆࡍࠬઞ"))).lower() == bstack1ll1_opy_ (u"ࠪࡸࡷࡻࡥࠨટ") and str(os.getenv(bstack1ll1_opy_ (u"࡙ࠫࡘࡁࡗࡋࡖࠫઠ"))).lower() == bstack1ll1_opy_ (u"ࠬࡺࡲࡶࡧࠪડ"):
    return os.getenv(bstack1ll1_opy_ (u"࠭ࡔࡓࡃ࡙ࡍࡘࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠬઢ"), 0)
  if str(os.getenv(bstack1ll1_opy_ (u"ࠧࡄࡋࠪણ"))).lower() == bstack1ll1_opy_ (u"ࠨࡶࡵࡹࡪ࠭ત") and str(os.getenv(bstack1ll1_opy_ (u"ࠩࡆࡍࡤࡔࡁࡎࡇࠪથ"))).lower() == bstack1ll1_opy_ (u"ࠪࡧࡴࡪࡥࡴࡪ࡬ࡴࠬદ"):
    return 0 # bstack1ll111111_opy_ bstack1l1lll1l_opy_ not set build number env
  if os.getenv(bstack1ll1_opy_ (u"ࠫࡇࡏࡔࡃࡗࡆࡏࡊ࡚࡟ࡃࡔࡄࡒࡈࡎࠧધ")) and os.getenv(bstack1ll1_opy_ (u"ࠬࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡅࡒࡑࡒࡏࡔࠨન")):
    return os.getenv(bstack1ll1_opy_ (u"࠭ࡂࡊࡖࡅ࡙ࡈࡑࡅࡕࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠨ઩"), 0)
  if str(os.getenv(bstack1ll1_opy_ (u"ࠧࡄࡋࠪપ"))).lower() == bstack1ll1_opy_ (u"ࠨࡶࡵࡹࡪ࠭ફ") and str(os.getenv(bstack1ll1_opy_ (u"ࠩࡇࡖࡔࡔࡅࠨબ"))).lower() == bstack1ll1_opy_ (u"ࠪࡸࡷࡻࡥࠨભ"):
    return os.getenv(bstack1ll1_opy_ (u"ࠫࡉࡘࡏࡏࡇࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠩમ"), 0)
  if str(os.getenv(bstack1ll1_opy_ (u"ࠬࡉࡉࠨય"))).lower() == bstack1ll1_opy_ (u"࠭ࡴࡳࡷࡨࠫર") and str(os.getenv(bstack1ll1_opy_ (u"ࠧࡔࡇࡐࡅࡕࡎࡏࡓࡇࠪ઱"))).lower() == bstack1ll1_opy_ (u"ࠨࡶࡵࡹࡪ࠭લ"):
    return os.getenv(bstack1ll1_opy_ (u"ࠩࡖࡉࡒࡇࡐࡉࡑࡕࡉࡤࡐࡏࡃࡡࡌࡈࠬળ"), 0)
  if str(os.getenv(bstack1ll1_opy_ (u"ࠪࡇࡎ࠭઴"))).lower() == bstack1ll1_opy_ (u"ࠫࡹࡸࡵࡦࠩવ") and str(os.getenv(bstack1ll1_opy_ (u"ࠬࡍࡉࡕࡎࡄࡆࡤࡉࡉࠨશ"))).lower() == bstack1ll1_opy_ (u"࠭ࡴࡳࡷࡨࠫષ"):
    return os.getenv(bstack1ll1_opy_ (u"ࠧࡄࡋࡢࡎࡔࡈ࡟ࡊࡆࠪસ"), 0)
  if str(os.getenv(bstack1ll1_opy_ (u"ࠨࡅࡌࠫહ"))).lower() == bstack1ll1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧ઺") and str(os.getenv(bstack1ll1_opy_ (u"ࠪࡆ࡚ࡏࡌࡅࡍࡌࡘࡊ࠭઻"))).lower() == bstack1ll1_opy_ (u"ࠫࡹࡸࡵࡦ઼ࠩ"):
    return os.getenv(bstack1ll1_opy_ (u"ࠬࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠧઽ"), 0)
  if str(os.getenv(bstack1ll1_opy_ (u"࠭ࡔࡇࡡࡅ࡙ࡎࡒࡄࠨા"))).lower() == bstack1ll1_opy_ (u"ࠧࡵࡴࡸࡩࠬિ"):
    return os.getenv(bstack1ll1_opy_ (u"ࠨࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡏࡄࠨી"), 0)
  return -1
def bstack1ll111l_opy_(bstack1ll11l_opy_):
  global CONFIG
  if not bstack1ll1_opy_ (u"ࠩࠧࡿࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࢀࠫુ") in CONFIG[bstack1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬૂ")]:
    return
  CONFIG[bstack1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ૃ")] = CONFIG[bstack1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧૄ")].replace(
    bstack1ll1_opy_ (u"࠭ࠤࡼࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࡽࠨૅ"),
    str(bstack1ll11l_opy_)
  )
def bstack1ll1l111_opy_():
  global CONFIG
  if not bstack1ll1_opy_ (u"ࠧࠥࡽࡇࡅ࡙ࡋ࡟ࡕࡋࡐࡉࢂ࠭૆") in CONFIG[bstack1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪે")]:
    return
  bstack1lll11l1l_opy_ = datetime.datetime.now()
  bstack1lll11l11_opy_ = bstack1lll11l1l_opy_.strftime(bstack1ll1_opy_ (u"ࠩࠨࡨ࠲ࠫࡢ࠮ࠧࡋ࠾ࠪࡓࠧૈ"))
  CONFIG[bstack1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬૉ")] = CONFIG[bstack1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭૊")].replace(
    bstack1ll1_opy_ (u"ࠬࠪࡻࡅࡃࡗࡉࡤ࡚ࡉࡎࡇࢀࠫો"),
    bstack1lll11l11_opy_
  )
def bstack1l1l1_opy_():
  global CONFIG
  if bstack1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨૌ") in CONFIG and not bool(CONFIG[bstack1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳ્ࠩ")]):
    del CONFIG[bstack1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ૎")]
    return
  if not bstack1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ૏") in CONFIG:
    CONFIG[bstack1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬૐ")] = bstack1ll1_opy_ (u"ࠫࠨࠪࡻࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࢃࠧ૑")
  if bstack1ll1_opy_ (u"ࠬࠪࡻࡅࡃࡗࡉࡤ࡚ࡉࡎࡇࢀࠫ૒") in CONFIG[bstack1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ૓")]:
    bstack1ll1l111_opy_()
    os.environ[bstack1ll1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑ࡟ࡄࡑࡐࡆࡎࡔࡅࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫ૔")] = CONFIG[bstack1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ૕")]
  if not bstack1ll1_opy_ (u"ࠩࠧࡿࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࢀࠫ૖") in CONFIG[bstack1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ૗")]:
    return
  bstack1ll11l_opy_ = bstack1ll1_opy_ (u"ࠫࠬ૘")
  bstack1ll1l1l1l_opy_ = bstack1lll1l11_opy_()
  if bstack1ll1l1l1l_opy_ != -1:
    bstack1ll11l_opy_ = bstack1ll1_opy_ (u"ࠬࡉࡉࠡࠩ૙") + str(bstack1ll1l1l1l_opy_)
  if bstack1ll11l_opy_ == bstack1ll1_opy_ (u"࠭ࠧ૚"):
    bstack11l1111_opy_ = bstack1ll111l1_opy_(CONFIG[bstack1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ૛")])
    if bstack11l1111_opy_ != -1:
      bstack1ll11l_opy_ = str(bstack11l1111_opy_)
  if bstack1ll11l_opy_:
    bstack1ll111l_opy_(bstack1ll11l_opy_)
    os.environ[bstack1ll1_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡠࡅࡒࡑࡇࡏࡎࡆࡆࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠬ૜")] = CONFIG[bstack1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ૝")]
def bstack1ll1l1111_opy_(bstack1ll1l1l1_opy_, bstack111l1l1_opy_, path):
  bstack1l1lll1_opy_ = {
    bstack1ll1_opy_ (u"ࠪ࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ૞"): bstack111l1l1_opy_
  }
  if os.path.exists(path):
    bstack1111ll1_opy_ = json.load(open(path, bstack1ll1_opy_ (u"ࠫࡷࡨࠧ૟")))
  else:
    bstack1111ll1_opy_ = {}
  bstack1111ll1_opy_[bstack1ll1l1l1_opy_] = bstack1l1lll1_opy_
  with open(path, bstack1ll1_opy_ (u"ࠧࡽࠫࠣૠ")) as outfile:
    json.dump(bstack1111ll1_opy_, outfile)
def bstack1ll111l1_opy_(bstack1ll1l1l1_opy_):
  bstack1ll1l1l1_opy_ = str(bstack1ll1l1l1_opy_)
  bstack11ll11ll_opy_ = os.path.join(os.path.expanduser(bstack1ll1_opy_ (u"࠭ࡾࠨૡ")), bstack1ll1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧૢ"))
  try:
    if not os.path.exists(bstack11ll11ll_opy_):
      os.makedirs(bstack11ll11ll_opy_)
    file_path = os.path.join(os.path.expanduser(bstack1ll1_opy_ (u"ࠨࢀࠪૣ")), bstack1ll1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ૤"), bstack1ll1_opy_ (u"ࠪ࠲ࡧࡻࡩ࡭ࡦ࠰ࡲࡦࡳࡥ࠮ࡥࡤࡧ࡭࡫࠮࡫ࡵࡲࡲࠬ૥"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack1ll1_opy_ (u"ࠫࡼ࠭૦")):
        pass
      with open(file_path, bstack1ll1_opy_ (u"ࠧࡽࠫࠣ૧")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack1ll1_opy_ (u"࠭ࡲࠨ૨")) as bstack1llll1l_opy_:
      bstack1ll1l_opy_ = json.load(bstack1llll1l_opy_)
    if bstack1ll1l1l1_opy_ in bstack1ll1l_opy_:
      bstack1ll1l11ll_opy_ = bstack1ll1l_opy_[bstack1ll1l1l1_opy_][bstack1ll1_opy_ (u"ࠧࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ૩")]
      bstack1l11ll1l1_opy_ = int(bstack1ll1l11ll_opy_) + 1
      bstack1ll1l1111_opy_(bstack1ll1l1l1_opy_, bstack1l11ll1l1_opy_, file_path)
      return bstack1l11ll1l1_opy_
    else:
      bstack1ll1l1111_opy_(bstack1ll1l1l1_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warn(bstack11111l_opy_.format(str(e)))
    return -1
def bstack1ll1l111l_opy_(config):
  if not config[bstack1ll1_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪ૪")] or not config[bstack1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬ૫")]:
    return True
  else:
    return False
def bstack1l11l1_opy_(config):
  if bstack1ll1llll_opy_() < version.parse(bstack1ll1_opy_ (u"ࠪ࠷࠳࠺࠮࠱ࠩ૬")):
    return False
  if bstack1ll1llll_opy_() >= version.parse(bstack1ll1_opy_ (u"ࠫ࠹࠴࠱࠯࠷ࠪ૭")):
    return True
  if bstack1ll1_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬ૮") in config and config[bstack1ll1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭૯")] == False:
    return False
  else:
    return True
def bstack1111l_opy_(config, index = 0):
  global bstack1ll11111l_opy_
  bstack11l1l111_opy_ = {}
  caps = bstack1llll_opy_ + bstack111ll_opy_
  if bstack1ll11111l_opy_:
    caps += bstack1l11l1lll_opy_
  for key in config:
    if key in caps + [bstack1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ૰")]:
      continue
    bstack11l1l111_opy_[key] = config[key]
  if bstack1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ૱") in config:
    for bstack111ll1ll_opy_ in config[bstack1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ૲")][index]:
      if bstack111ll1ll_opy_ in caps + [bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨ૳"), bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬ૴")]:
        continue
      bstack11l1l111_opy_[bstack111ll1ll_opy_] = config[bstack1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ૵")][index][bstack111ll1ll_opy_]
  bstack11l1l111_opy_[bstack1ll1_opy_ (u"࠭ࡨࡰࡵࡷࡒࡦࡳࡥࠨ૶")] = socket.gethostname()
  if bstack1ll1_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨ૷") in bstack11l1l111_opy_:
    del(bstack11l1l111_opy_[bstack1ll1_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࠩ૸")])
  return bstack11l1l111_opy_
def bstack1l1l11l11_opy_(config):
  global bstack1ll11111l_opy_
  bstack11ll1l11_opy_ = {}
  caps = bstack111ll_opy_
  if bstack1ll11111l_opy_:
    caps+= bstack1l11l1lll_opy_
  for key in caps:
    if key in config:
      bstack11ll1l11_opy_[key] = config[key]
  return bstack11ll1l11_opy_
def bstack1ll111l11_opy_(bstack11l1l111_opy_, bstack11ll1l11_opy_):
  bstack1llll11ll_opy_ = {}
  for key in bstack11l1l111_opy_.keys():
    if key in bstack111l11l_opy_:
      bstack1llll11ll_opy_[bstack111l11l_opy_[key]] = bstack11l1l111_opy_[key]
    else:
      bstack1llll11ll_opy_[key] = bstack11l1l111_opy_[key]
  for key in bstack11ll1l11_opy_:
    if key in bstack111l11l_opy_:
      bstack1llll11ll_opy_[bstack111l11l_opy_[key]] = bstack11ll1l11_opy_[key]
    else:
      bstack1llll11ll_opy_[key] = bstack11ll1l11_opy_[key]
  return bstack1llll11ll_opy_
def bstack1llll11l1_opy_(config, index = 0):
  global bstack1ll11111l_opy_
  caps = {}
  bstack11ll1l11_opy_ = bstack1l1l11l11_opy_(config)
  bstack1l111l11_opy_ = bstack111ll_opy_
  bstack1l111l11_opy_ += bstack11111l11_opy_
  if bstack1ll11111l_opy_:
    bstack1l111l11_opy_ += bstack1l11l1lll_opy_
  if bstack1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬૹ") in config:
    if bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨૺ") in config[bstack1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧૻ")][index]:
      caps[bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪૼ")] = config[bstack1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ૽")][index][bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ૾")]
    if bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ૿") in config[bstack1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ଀")][index]:
      caps[bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫଁ")] = str(config[bstack1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧଂ")][index][bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ଃ")])
    bstack1111l11_opy_ = {}
    for bstack11111111_opy_ in bstack1l111l11_opy_:
      if bstack11111111_opy_ in config[bstack1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ଄")][index]:
        if bstack11111111_opy_ == bstack1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩଅ"):
          bstack1111l11_opy_[bstack11111111_opy_] = str(config[bstack1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫଆ")][index][bstack11111111_opy_] * 1.0)
        else:
          bstack1111l11_opy_[bstack11111111_opy_] = config[bstack1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬଇ")][index][bstack11111111_opy_]
        del(config[bstack1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଈ")][index][bstack11111111_opy_])
    bstack11ll1l11_opy_ = update(bstack11ll1l11_opy_, bstack1111l11_opy_)
  bstack11l1l111_opy_ = bstack1111l_opy_(config, index)
  for bstack1lllll1l1_opy_ in bstack111ll_opy_ + [bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩଉ"), bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ଊ")]:
    if bstack1lllll1l1_opy_ in bstack11l1l111_opy_:
      bstack11ll1l11_opy_[bstack1lllll1l1_opy_] = bstack11l1l111_opy_[bstack1lllll1l1_opy_]
      del(bstack11l1l111_opy_[bstack1lllll1l1_opy_])
  if bstack1l11l1_opy_(config):
    bstack11l1l111_opy_[bstack1ll1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ଋ")] = True
    caps.update(bstack11ll1l11_opy_)
    caps[bstack1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨଌ")] = bstack11l1l111_opy_
  else:
    bstack11l1l111_opy_[bstack1ll1_opy_ (u"ࠨࡷࡶࡩ࡜࠹ࡃࠨ଍")] = False
    caps.update(bstack1ll111l11_opy_(bstack11l1l111_opy_, bstack11ll1l11_opy_))
    if bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ଎") in caps:
      caps[bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫଏ")] = caps[bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩଐ")]
      del(caps[bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ଑")])
    if bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ଒") in caps:
      caps[bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩଓ")] = caps[bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩଔ")]
      del(caps[bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪକ")])
  return caps
def bstack1l1l11ll_opy_():
  if bstack1ll1llll_opy_() <= version.parse(bstack1ll1_opy_ (u"ࠪ࠷࠳࠷࠳࠯࠲ࠪଖ")):
    return bstack1l1ll111l_opy_
  return bstack11lll1_opy_
def bstack11l1lll1_opy_(options):
  return hasattr(options, bstack1ll1_opy_ (u"ࠫࡸ࡫ࡴࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷࡽࠬଗ"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1llll1l1l_opy_(options, bstack1l11ll11l_opy_):
  for bstack1llllll_opy_ in bstack1l11ll11l_opy_:
    if bstack1llllll_opy_ in [bstack1ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪଘ"), bstack1ll1_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪଙ")]:
      next
    if bstack1llllll_opy_ in options._experimental_options:
      options._experimental_options[bstack1llllll_opy_]= update(options._experimental_options[bstack1llllll_opy_], bstack1l11ll11l_opy_[bstack1llllll_opy_])
    else:
      options.add_experimental_option(bstack1llllll_opy_, bstack1l11ll11l_opy_[bstack1llllll_opy_])
  if bstack1ll1_opy_ (u"ࠧࡢࡴࡪࡷࠬଚ") in bstack1l11ll11l_opy_:
    for arg in bstack1l11ll11l_opy_[bstack1ll1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ଛ")]:
      options.add_argument(arg)
    del(bstack1l11ll11l_opy_[bstack1ll1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧଜ")])
  if bstack1ll1_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧଝ") in bstack1l11ll11l_opy_:
    for ext in bstack1l11ll11l_opy_[bstack1ll1_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨଞ")]:
      options.add_extension(ext)
    del(bstack1l11ll11l_opy_[bstack1ll1_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩଟ")])
def bstack1llll1l1_opy_(options, bstack11l111l_opy_):
  if bstack1ll1_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬଠ") in bstack11l111l_opy_:
    for bstack1ll1lll1l_opy_ in bstack11l111l_opy_[bstack1ll1_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭ଡ")]:
      if bstack1ll1lll1l_opy_ in options._preferences:
        options._preferences[bstack1ll1lll1l_opy_] = update(options._preferences[bstack1ll1lll1l_opy_], bstack11l111l_opy_[bstack1ll1_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧଢ")][bstack1ll1lll1l_opy_])
      else:
        options.set_preference(bstack1ll1lll1l_opy_, bstack11l111l_opy_[bstack1ll1_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨଣ")][bstack1ll1lll1l_opy_])
  if bstack1ll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨତ") in bstack11l111l_opy_:
    for arg in bstack11l111l_opy_[bstack1ll1_opy_ (u"ࠫࡦࡸࡧࡴࠩଥ")]:
      options.add_argument(arg)
def bstack1lll1ll1l_opy_(options, bstack111l1l1l_opy_):
  if bstack1ll1_opy_ (u"ࠬࡽࡥࡣࡸ࡬ࡩࡼ࠭ଦ") in bstack111l1l1l_opy_:
    options.use_webview(bool(bstack111l1l1l_opy_[bstack1ll1_opy_ (u"࠭ࡷࡦࡤࡹ࡭ࡪࡽࠧଧ")]))
  bstack1llll1l1l_opy_(options, bstack111l1l1l_opy_)
def bstack1ll11l1l_opy_(options, bstack1lll11l1_opy_):
  for bstack11l1l_opy_ in bstack1lll11l1_opy_:
    if bstack11l1l_opy_ in [bstack1ll1_opy_ (u"ࠧࡵࡧࡦ࡬ࡳࡵ࡬ࡰࡩࡼࡔࡷ࡫ࡶࡪࡧࡺࠫନ"), bstack1ll1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭଩")]:
      next
    options.set_capability(bstack11l1l_opy_, bstack1lll11l1_opy_[bstack11l1l_opy_])
  if bstack1ll1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧପ") in bstack1lll11l1_opy_:
    for arg in bstack1lll11l1_opy_[bstack1ll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨଫ")]:
      options.add_argument(arg)
  if bstack1ll1_opy_ (u"ࠫࡹ࡫ࡣࡩࡰࡲࡰࡴ࡭ࡹࡑࡴࡨࡺ࡮࡫ࡷࠨବ") in bstack1lll11l1_opy_:
    options.use_technology_preview(bool(bstack1lll11l1_opy_[bstack1ll1_opy_ (u"ࠬࡺࡥࡤࡪࡱࡳࡱࡵࡧࡺࡒࡵࡩࡻ࡯ࡥࡸࠩଭ")]))
def bstack1l1ll1l1_opy_(options, bstack111l111_opy_):
  for bstack1ll1111ll_opy_ in bstack111l111_opy_:
    if bstack1ll1111ll_opy_ in [bstack1ll1_opy_ (u"࠭ࡡࡥࡦ࡬ࡸ࡮ࡵ࡮ࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪମ"), bstack1ll1_opy_ (u"ࠧࡢࡴࡪࡷࠬଯ")]:
      next
    options._options[bstack1ll1111ll_opy_] = bstack111l111_opy_[bstack1ll1111ll_opy_]
  if bstack1ll1_opy_ (u"ࠨࡣࡧࡨ࡮ࡺࡩࡰࡰࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬର") in bstack111l111_opy_:
    for bstack1l111lll_opy_ in bstack111l111_opy_[bstack1ll1_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭଱")]:
      options.add_additional_option(
          bstack1l111lll_opy_, bstack111l111_opy_[bstack1ll1_opy_ (u"ࠪࡥࡩࡪࡩࡵ࡫ࡲࡲࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧଲ")][bstack1l111lll_opy_])
  if bstack1ll1_opy_ (u"ࠫࡦࡸࡧࡴࠩଳ") in bstack111l111_opy_:
    for arg in bstack111l111_opy_[bstack1ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪ଴")]:
      options.add_argument(arg)
def bstack1l11ll111_opy_(options, caps):
  if not hasattr(options, bstack1ll1_opy_ (u"࠭ࡋࡆ࡛ࠪଵ")):
    return
  if options.KEY == bstack1ll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬଶ") and options.KEY in caps:
    bstack1llll1l1l_opy_(options, caps[bstack1ll1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ଷ")])
  elif options.KEY == bstack1ll1_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧସ") and options.KEY in caps:
    bstack1llll1l1_opy_(options, caps[bstack1ll1_opy_ (u"ࠪࡱࡴࢀ࠺ࡧ࡫ࡵࡩ࡫ࡵࡸࡐࡲࡷ࡭ࡴࡴࡳࠨହ")])
  elif options.KEY == bstack1ll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬ଺") and options.KEY in caps:
    bstack1ll11l1l_opy_(options, caps[bstack1ll1_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭଻")])
  elif options.KEY == bstack1ll1_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹ଼ࠧ") and options.KEY in caps:
    bstack1lll1ll1l_opy_(options, caps[bstack1ll1_opy_ (u"ࠧ࡮ࡵ࠽ࡩࡩ࡭ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨଽ")])
  elif options.KEY == bstack1ll1_opy_ (u"ࠨࡵࡨ࠾࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧା") and options.KEY in caps:
    bstack1l1ll1l1_opy_(options, caps[bstack1ll1_opy_ (u"ࠩࡶࡩ࠿࡯ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨି")])
def bstack11l11ll_opy_(caps):
  global bstack1ll11111l_opy_
  if bstack1ll11111l_opy_:
    if bstack1lllll1_opy_() < version.parse(bstack1ll1_opy_ (u"ࠪ࠶࠳࠹࠮࠱ࠩୀ")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack1ll1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࠫୁ")
    if bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪୂ") in caps:
      browser = caps[bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫୃ")]
    elif bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨୄ") in caps:
      browser = caps[bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࠩ୅")]
    browser = str(browser).lower()
    if browser == bstack1ll1_opy_ (u"ࠩ࡬ࡴ࡭ࡵ࡮ࡦࠩ୆") or browser == bstack1ll1_opy_ (u"ࠪ࡭ࡵࡧࡤࠨେ"):
      browser = bstack1ll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬ࠫୈ")
    if browser == bstack1ll1_opy_ (u"ࠬࡹࡡ࡮ࡵࡸࡲ࡬࠭୉"):
      browser = bstack1ll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭୊")
    if browser not in [bstack1ll1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࠧୋ"), bstack1ll1_opy_ (u"ࠨࡧࡧ࡫ࡪ࠭ୌ"), bstack1ll1_opy_ (u"ࠩ࡬ࡩ୍ࠬ"), bstack1ll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪ୎"), bstack1ll1_opy_ (u"ࠫ࡫࡯ࡲࡦࡨࡲࡼࠬ୏")]:
      return None
    try:
      package = bstack1ll1_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠮ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴ࠱ࡿࢂ࠴࡯ࡱࡶ࡬ࡳࡳࡹࠧ୐").format(browser)
      name = bstack1ll1_opy_ (u"࠭ࡏࡱࡶ࡬ࡳࡳࡹࠧ୑")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack11l1lll1_opy_(options):
        return None
      for bstack1lllll1l1_opy_ in caps.keys():
        options.set_capability(bstack1lllll1l1_opy_, caps[bstack1lllll1l1_opy_])
      bstack1l11ll111_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack1llllllll_opy_(options, bstack11l1l1l1_opy_):
  if not bstack11l1lll1_opy_(options):
    return
  for bstack1lllll1l1_opy_ in bstack11l1l1l1_opy_.keys():
    if bstack1lllll1l1_opy_ in bstack11111l11_opy_:
      next
    if bstack1lllll1l1_opy_ in options._caps and type(options._caps[bstack1lllll1l1_opy_]) in [dict, list]:
      options._caps[bstack1lllll1l1_opy_] = update(options._caps[bstack1lllll1l1_opy_], bstack11l1l1l1_opy_[bstack1lllll1l1_opy_])
    else:
      options.set_capability(bstack1lllll1l1_opy_, bstack11l1l1l1_opy_[bstack1lllll1l1_opy_])
  bstack1l11ll111_opy_(options, bstack11l1l1l1_opy_)
  if bstack1ll1_opy_ (u"ࠧ࡮ࡱࡽ࠾ࡩ࡫ࡢࡶࡩࡪࡩࡷࡇࡤࡥࡴࡨࡷࡸ࠭୒") in options._caps:
    if options._caps[bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭୓")] and options._caps[bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ୔")].lower() != bstack1ll1_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫ୕"):
      del options._caps[bstack1ll1_opy_ (u"ࠫࡲࡵࡺ࠻ࡦࡨࡦࡺ࡭ࡧࡦࡴࡄࡨࡩࡸࡥࡴࡵࠪୖ")]
def bstack1l11lll_opy_(proxy_config):
  if bstack1ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩୗ") in proxy_config:
    proxy_config[bstack1ll1_opy_ (u"࠭ࡳࡴ࡮ࡓࡶࡴࡾࡹࠨ୘")] = proxy_config[bstack1ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫ୙")]
    del(proxy_config[bstack1ll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ୚")])
  if bstack1ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬ୛") in proxy_config and proxy_config[bstack1ll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡖࡼࡴࡪ࠭ଡ଼")].lower() != bstack1ll1_opy_ (u"ࠫࡩ࡯ࡲࡦࡥࡷࠫଢ଼"):
    proxy_config[bstack1ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡘࡾࡶࡥࠨ୞")] = bstack1ll1_opy_ (u"࠭࡭ࡢࡰࡸࡥࡱ࠭ୟ")
  if bstack1ll1_opy_ (u"ࠧࡱࡴࡲࡼࡾࡇࡵࡵࡱࡦࡳࡳ࡬ࡩࡨࡗࡵࡰࠬୠ") in proxy_config:
    proxy_config[bstack1ll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫୡ")] = bstack1ll1_opy_ (u"ࠩࡳࡥࡨ࠭ୢ")
  return proxy_config
def bstack1ll1l11l1_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack1ll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩୣ") in config:
    return proxy
  config[bstack1ll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪ୤")] = bstack1l11lll_opy_(config[bstack1ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫ୥")])
  if proxy == None:
    proxy = Proxy(config[bstack1ll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࠬ୦")])
  return proxy
def bstack111l1ll1_opy_(self):
  global CONFIG
  global bstack111lll1l_opy_
  if bstack1ll1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪ୧") in CONFIG:
    return CONFIG[bstack1ll1_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫ୨")]
  elif bstack1ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭୩") in CONFIG:
    return CONFIG[bstack1ll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧ୪")]
  else:
    return bstack111lll1l_opy_(self)
def bstack11l1l1ll_opy_():
  global CONFIG
  return bstack1ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧ୫") in CONFIG or bstack1ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩ୬") in CONFIG
def bstack111l1111_opy_(config):
  if not bstack11l1l1ll_opy_():
    return
  if config.get(bstack1ll1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩ୭")):
    return config.get(bstack1ll1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪ୮"))
  if config.get(bstack1ll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ୯")):
    return config.get(bstack1ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭୰"))
def bstack1ll1l1ll_opy_():
  return bstack11l1l1ll_opy_() and bstack1ll1llll_opy_() >= version.parse(bstack1lllll1l_opy_)
def bstack1ll11l11l_opy_(config):
  if bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧୱ") in config:
    return config[bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨ୲")]
  if bstack1ll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫ୳") in config:
    return config[bstack1ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ୴")]
  return {}
def bstack11l1l1l_opy_(caps):
  global bstack111l1lll_opy_
  if bstack1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨ୵") in caps:
    caps[bstack1ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ୶")][bstack1ll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࠨ୷")] = True
    if bstack111l1lll_opy_:
      caps[bstack1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ୸")][bstack1ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭୹")] = bstack111l1lll_opy_
  else:
    caps[bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࠪ୺")] = True
    if bstack111l1lll_opy_:
      caps[bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ୻")] = bstack111l1lll_opy_
def bstack1l1l1111l_opy_():
  global CONFIG
  if bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ୼") in CONFIG and CONFIG[bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ୽")]:
    bstack1ll1ll1_opy_ = bstack1ll11l11l_opy_(CONFIG)
    bstack1lll1111_opy_(CONFIG[bstack1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬ୾")], bstack1ll1ll1_opy_)
def bstack1lll1111_opy_(key, bstack1ll1ll1_opy_):
  global bstack11llll11_opy_
  logger.info(bstack1l111l1_opy_)
  try:
    bstack11llll11_opy_ = Local()
    bstack11ll_opy_ = {bstack1ll1_opy_ (u"ࠪ࡯ࡪࡿࠧ୿"): key}
    bstack11ll_opy_.update(bstack1ll1ll1_opy_)
    logger.debug(bstack11l1ll1l_opy_.format(str(bstack11ll_opy_)))
    bstack11llll11_opy_.start(**bstack11ll_opy_)
    if bstack11llll11_opy_.isRunning():
      logger.info(bstack1ll11ll1_opy_)
  except Exception as e:
    bstack1ll1lll_opy_(bstack1llll1ll_opy_.format(str(e)))
def bstack1lllll1ll_opy_():
  global bstack11llll11_opy_
  if bstack11llll11_opy_.isRunning():
    logger.info(bstack1l11l111_opy_)
    bstack11llll11_opy_.stop()
  bstack11llll11_opy_ = None
def bstack1l1l11l1l_opy_():
  global bstack1l1ll_opy_
  global bstack111l_opy_
  if bstack1l1ll_opy_:
    logger.warning(bstack1111111l_opy_.format(str(bstack1l1ll_opy_)))
  logger.info(bstack1l11l11l_opy_)
  global bstack11llll11_opy_
  if bstack11llll11_opy_:
    bstack1lllll1ll_opy_()
  try:
    for driver in bstack111l_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack1l11lllll_opy_)
  bstack11111l1_opy_()
def bstack1l1llll11_opy_(self, *args):
  logger.error(bstack1l1l11l1_opy_)
  bstack1l1l11l1l_opy_()
  sys.exit(1)
def bstack1ll1lll_opy_(err):
  logger.critical(bstack111ll11_opy_.format(str(err)))
  bstack11111l1_opy_(bstack111ll11_opy_.format(str(err)))
  atexit.unregister(bstack1l1l11l1l_opy_)
  sys.exit(1)
def bstack11l1_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack11111l1_opy_(message)
  atexit.unregister(bstack1l1l11l1l_opy_)
  sys.exit(1)
def bstack1lll1ll11_opy_():
  global CONFIG
  global bstack1111l1l_opy_
  global bstack1lll1111l_opy_
  global bstack111lllll_opy_
  CONFIG = bstack1l1ll1ll_opy_()
  bstack1lll1ll1_opy_()
  bstack1l11l_opy_()
  CONFIG = bstack1ll11lll_opy_(CONFIG)
  update(CONFIG, bstack1lll1111l_opy_)
  update(CONFIG, bstack1111l1l_opy_)
  CONFIG = bstack1ll111lll_opy_(CONFIG)
  if bstack1ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ஀") in CONFIG and str(CONFIG[bstack1ll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩ஁")]).lower() == bstack1ll1_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬஂ"):
    bstack111lllll_opy_ = False
  if (bstack1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪஃ") in CONFIG and bstack1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ஄") in bstack1111l1l_opy_) or (bstack1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬஅ") in CONFIG and bstack1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ஆ") not in bstack1lll1111l_opy_):
    if os.getenv(bstack1ll1_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨஇ")):
      CONFIG[bstack1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧஈ")] = os.getenv(bstack1ll1_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡥࡃࡐࡏࡅࡍࡓࡋࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪஉ"))
    else:
      bstack1l1l1_opy_()
  elif (bstack1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪஊ") not in CONFIG and bstack1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ஋") in CONFIG) or (bstack1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ஌") in bstack1lll1111l_opy_ and bstack1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭஍") not in bstack1111l1l_opy_):
    del(CONFIG[bstack1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭எ")])
  if bstack1ll1l111l_opy_(CONFIG):
    bstack1ll1lll_opy_(bstack11l1llll_opy_)
  bstack11l1ll1_opy_()
  bstack1ll11llll_opy_()
  if bstack1ll11111l_opy_:
    CONFIG[bstack1ll1_opy_ (u"ࠬࡧࡰࡱࠩஏ")] = bstack1l11ll1_opy_(CONFIG)
    logger.info(bstack1l11l11_opy_.format(CONFIG[bstack1ll1_opy_ (u"࠭ࡡࡱࡲࠪஐ")]))
def bstack1ll11llll_opy_():
  global CONFIG
  global bstack1ll11111l_opy_
  if bstack1ll1_opy_ (u"ࠧࡢࡲࡳࠫ஑") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack11l1_opy_(e, bstack1l11lll1l_opy_)
    bstack1ll11111l_opy_ = True
def bstack1l11ll1_opy_(config):
  bstack1111l111_opy_ = bstack1ll1_opy_ (u"ࠨࠩஒ")
  app = config[bstack1ll1_opy_ (u"ࠩࡤࡴࡵ࠭ஓ")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack1l1l1l1_opy_:
      if os.path.exists(app):
        bstack1111l111_opy_ = bstack11111lll_opy_(config, app)
      elif bstack1ll1l11_opy_(app):
        bstack1111l111_opy_ = app
      else:
        bstack1ll1lll_opy_(bstack111ll11l_opy_.format(app))
    else:
      if bstack1ll1l11_opy_(app):
        bstack1111l111_opy_ = app
      elif os.path.exists(app):
        bstack1111l111_opy_ = bstack11111lll_opy_(app)
      else:
        bstack1ll1lll_opy_(bstack111ll1l1_opy_)
  else:
    if len(app) > 2:
      bstack1ll1lll_opy_(bstack1ll11ll_opy_)
    elif len(app) == 2:
      if bstack1ll1_opy_ (u"ࠪࡴࡦࡺࡨࠨஔ") in app and bstack1ll1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡣ࡮ࡪࠧக") in app:
        if os.path.exists(app[bstack1ll1_opy_ (u"ࠬࡶࡡࡵࡪࠪ஖")]):
          bstack1111l111_opy_ = bstack11111lll_opy_(config, app[bstack1ll1_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ஗")], app[bstack1ll1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠪ஘")])
        else:
          bstack1ll1lll_opy_(bstack111ll11l_opy_.format(app))
      else:
        bstack1ll1lll_opy_(bstack1ll11ll_opy_)
    else:
      for key in app:
        if key in bstack1l11l1l1l_opy_:
          if key == bstack1ll1_opy_ (u"ࠨࡲࡤࡸ࡭࠭ங"):
            if os.path.exists(app[key]):
              bstack1111l111_opy_ = bstack11111lll_opy_(config, app[key])
            else:
              bstack1ll1lll_opy_(bstack111ll11l_opy_.format(app))
          else:
            bstack1111l111_opy_ = app[key]
        else:
          bstack1ll1lll_opy_(bstack1l1ll1l1l_opy_)
  return bstack1111l111_opy_
def bstack1ll1l11_opy_(bstack1111l111_opy_):
  import re
  bstack1l1llllll_opy_ = re.compile(bstack1ll1_opy_ (u"ࡴࠥࡢࡠࡧ࠭ࡻࡃ࠰࡞࠵࠳࠹࡝ࡡ࠱ࡠ࠲ࡣࠪࠥࠤச"))
  bstack111l1_opy_ = re.compile(bstack1ll1_opy_ (u"ࡵࠦࡣࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫ࠱࡞ࡥ࠲ࢀࡁ࠮࡜࠳࠱࠾ࡢ࡟࠯࡞࠰ࡡ࠯ࠪࠢ஛"))
  if bstack1ll1_opy_ (u"ࠫࡧࡹ࠺࠰࠱ࠪஜ") in bstack1111l111_opy_ or re.fullmatch(bstack1l1llllll_opy_, bstack1111l111_opy_) or re.fullmatch(bstack111l1_opy_, bstack1111l111_opy_):
    return True
  else:
    return False
def bstack11111lll_opy_(config, path, bstack1l11l1l11_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack1ll1_opy_ (u"ࠬࡸࡢࠨ஝")).read()).hexdigest()
  bstack1ll11l1l1_opy_ = bstack1lll11l_opy_(md5_hash)
  bstack1111l111_opy_ = None
  if bstack1ll11l1l1_opy_:
    logger.info(bstack1llllll1l_opy_.format(bstack1ll11l1l1_opy_, md5_hash))
    return bstack1ll11l1l1_opy_
  bstack1ll1111l1_opy_ = MultipartEncoder(
    fields={
        bstack1ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࠫஞ"): (os.path.basename(path), open(os.path.abspath(path), bstack1ll1_opy_ (u"ࠧࡳࡤࠪட")), bstack1ll1_opy_ (u"ࠨࡶࡨࡼࡹ࠵ࡰ࡭ࡣ࡬ࡲࠬ஠")),
        bstack1ll1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡡ࡬ࡨࠬ஡"): bstack1l11l1l11_opy_
    }
  )
  response = requests.post(bstack1l1llll1_opy_, data=bstack1ll1111l1_opy_,
                         headers={bstack1ll1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩ஢"): bstack1ll1111l1_opy_.content_type}, auth=(config[bstack1ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ண")], config[bstack1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨத")]))
  try:
    res = json.loads(response.text)
    bstack1111l111_opy_ = res[bstack1ll1_opy_ (u"࠭ࡡࡱࡲࡢࡹࡷࡲࠧ஥")]
    logger.info(bstack11lllll1_opy_.format(bstack1111l111_opy_))
    bstack11ll1111_opy_(md5_hash, bstack1111l111_opy_)
  except ValueError as err:
    bstack1ll1lll_opy_(bstack111llll1_opy_.format(str(err)))
  return bstack1111l111_opy_
def bstack11l1ll1_opy_():
  global CONFIG
  global bstack1llll1_opy_
  bstack1lll1llll_opy_ = 0
  bstack11ll1_opy_ = 1
  if bstack1ll1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ஦") in CONFIG:
    bstack11ll1_opy_ = CONFIG[bstack1ll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ஧")]
  if bstack1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬந") in CONFIG:
    bstack1lll1llll_opy_ = len(CONFIG[bstack1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ன")])
  bstack1llll1_opy_ = int(bstack11ll1_opy_) * int(bstack1lll1llll_opy_)
def bstack1lll11l_opy_(md5_hash):
  bstack1l1ll111_opy_ = os.path.join(os.path.expanduser(bstack1ll1_opy_ (u"ࠫࢃ࠭ப")), bstack1ll1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ஫"), bstack1ll1_opy_ (u"࠭ࡡࡱࡲࡘࡴࡱࡵࡡࡥࡏࡇ࠹ࡍࡧࡳࡩ࠰࡭ࡷࡴࡴࠧ஬"))
  if os.path.exists(bstack1l1ll111_opy_):
    bstack1l111ll1_opy_ = json.load(open(bstack1l1ll111_opy_,bstack1ll1_opy_ (u"ࠧࡳࡤࠪ஭")))
    if md5_hash in bstack1l111ll1_opy_:
      bstack11l111_opy_ = bstack1l111ll1_opy_[md5_hash]
      bstack1l1l1ll11_opy_ = datetime.datetime.now()
      bstack1l1ll1ll1_opy_ = datetime.datetime.strptime(bstack11l111_opy_[bstack1ll1_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫம")], bstack1ll1_opy_ (u"ࠩࠨࡨ࠴ࠫ࡭࠰ࠧ࡜ࠤࠪࡎ࠺ࠦࡏ࠽ࠩࡘ࠭ய"))
      if (bstack1l1l1ll11_opy_ - bstack1l1ll1ll1_opy_).days > 60:
        return None
      elif version.parse(str(__version__)) > version.parse(bstack11l111_opy_[bstack1ll1_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨர")]):
        return None
      return bstack11l111_opy_[bstack1ll1_opy_ (u"ࠫ࡮ࡪࠧற")]
  else:
    return None
def bstack11ll1111_opy_(md5_hash, bstack1111l111_opy_):
  bstack11ll11ll_opy_ = os.path.join(os.path.expanduser(bstack1ll1_opy_ (u"ࠬࢄࠧல")), bstack1ll1_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ள"))
  if not os.path.exists(bstack11ll11ll_opy_):
    os.makedirs(bstack11ll11ll_opy_)
  bstack1l1ll111_opy_ = os.path.join(os.path.expanduser(bstack1ll1_opy_ (u"ࠧࡿࠩழ")), bstack1ll1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨவ"), bstack1ll1_opy_ (u"ࠩࡤࡴࡵ࡛ࡰ࡭ࡱࡤࡨࡒࡊ࠵ࡉࡣࡶ࡬࠳ࡰࡳࡰࡰࠪஶ"))
  bstack1l11ll1l_opy_ = {
    bstack1ll1_opy_ (u"ࠪ࡭ࡩ࠭ஷ"): bstack1111l111_opy_,
    bstack1ll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧஸ"): datetime.datetime.strftime(datetime.datetime.now(), bstack1ll1_opy_ (u"ࠬࠫࡤ࠰ࠧࡰ࠳ࠪ࡟ࠠࠦࡊ࠽ࠩࡒࡀࠥࡔࠩஹ")),
    bstack1ll1_opy_ (u"࠭ࡳࡥ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫ஺"): str(__version__)
  }
  if os.path.exists(bstack1l1ll111_opy_):
    bstack1l111ll1_opy_ = json.load(open(bstack1l1ll111_opy_,bstack1ll1_opy_ (u"ࠧࡳࡤࠪ஻")))
  else:
    bstack1l111ll1_opy_ = {}
  bstack1l111ll1_opy_[md5_hash] = bstack1l11ll1l_opy_
  with open(bstack1l1ll111_opy_, bstack1ll1_opy_ (u"ࠣࡹ࠮ࠦ஼")) as outfile:
    json.dump(bstack1l111ll1_opy_, outfile)
def bstack1lll11111_opy_(self):
  return
def bstack1llll1l11_opy_(self):
  return
def bstack111l11ll_opy_(self):
  from selenium.webdriver.remote.webdriver import WebDriver
  WebDriver.quit(self)
def bstack1llll1111_opy_(self, command_executor,
        desired_capabilities=None, browser_profile=None, proxy=None,
        keep_alive=True, file_detector=None, options=None):
  global CONFIG
  global bstack1111111_opy_
  global bstack1111ll_opy_
  global bstack1ll111ll_opy_
  global bstack1l1ll1l_opy_
  global bstack1l1l1l11_opy_
  global bstack1lll1_opy_
  global bstack111l_opy_
  CONFIG[bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫ஽")] = str(bstack1l1l1l11_opy_) + str(__version__)
  command_executor = bstack1l1l11ll_opy_()
  logger.debug(bstack1lll1ll_opy_.format(command_executor))
  proxy = bstack1ll1l11l1_opy_(CONFIG, proxy)
  bstack111111l_opy_ = 0 if bstack1111ll_opy_ < 0 else bstack1111ll_opy_
  if bstack1l1ll1l_opy_ is True:
    bstack111111l_opy_ = int(threading.current_thread().getName())
  bstack11l1l1l1_opy_ = bstack1llll11l1_opy_(CONFIG, bstack111111l_opy_)
  logger.debug(bstack11lll11_opy_.format(str(bstack11l1l1l1_opy_)))
  if bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧா") in CONFIG and CONFIG[bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨி")]:
    bstack11l1l1l_opy_(bstack11l1l1l1_opy_)
  if desired_capabilities:
    bstack11lll111_opy_ = bstack1ll11lll_opy_(desired_capabilities)
    bstack11lll111_opy_[bstack1ll1_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬீ")] = bstack1l11l1_opy_(CONFIG)
    bstack111ll111_opy_ = bstack1llll11l1_opy_(bstack11lll111_opy_)
    if bstack111ll111_opy_:
      bstack11l1l1l1_opy_ = update(bstack111ll111_opy_, bstack11l1l1l1_opy_)
    desired_capabilities = None
  if options:
    bstack1llllllll_opy_(options, bstack11l1l1l1_opy_)
  if not options:
    options = bstack11l11ll_opy_(bstack11l1l1l1_opy_)
  if options and bstack1ll1llll_opy_() >= version.parse(bstack1ll1_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬு")):
    desired_capabilities = None
  if (
      not options and not desired_capabilities
  ) or (
      bstack1ll1llll_opy_() < version.parse(bstack1ll1_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭ூ")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack11l1l1l1_opy_)
  logger.info(bstack1l1llll_opy_)
  if bstack1ll1llll_opy_() >= version.parse(bstack1ll1_opy_ (u"ࠨ࠵࠱࠼࠳࠶ࠧ௃")):
    bstack1lll1_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities, options=options,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1ll1llll_opy_() >= version.parse(bstack1ll1_opy_ (u"ࠩ࠵࠲࠺࠹࠮࠱ࠩ௄")):
    bstack1lll1_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive, file_detector=file_detector)
  else:
    bstack1lll1_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive)
  bstack1111111_opy_ = self.session_id
  bstack111l_opy_.append(self)
  if bstack1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭௅") in CONFIG and bstack1ll1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩெ") in CONFIG[bstack1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨே")][bstack111111l_opy_]:
    bstack1ll111ll_opy_ = CONFIG[bstack1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩை")][bstack111111l_opy_][bstack1ll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ௉")]
  logger.debug(bstack11lll11l_opy_.format(bstack1111111_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    def bstack111l11l1_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      if(bstack1ll1_opy_ (u"ࠣ࡫ࡱࡨࡪࡾ࠮࡫ࡵࠥொ") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack1ll1_opy_ (u"ࠩࢁࠫோ")), bstack1ll1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪௌ"), bstack1ll1_opy_ (u"ࠫ࠳ࡹࡥࡴࡵ࡬ࡳࡳ࡯ࡤࡴ࠰ࡷࡼࡹ்࠭")), bstack1ll1_opy_ (u"ࠬࡽࠧ௎")) as fp:
          fp.write(bstack1ll1_opy_ (u"ࠨࠢ௏"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack1ll1_opy_ (u"ࠢࡪࡰࡧࡩࡽࡥࡢࡴࡶࡤࡧࡰ࠴ࡪࡴࠤௐ")))):
          with open(args[1], bstack1ll1_opy_ (u"ࠨࡴࠪ௑")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack1ll1_opy_ (u"ࠩࡤࡷࡾࡴࡣࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡣࡳ࡫ࡷࡑࡣࡪࡩ࠭ࡩ࡯࡯ࡶࡨࡼࡹ࠲ࠠࡱࡣࡪࡩࠥࡃࠠࡷࡱ࡬ࡨࠥ࠶ࠩࠨ௒") in line), None)
            if index is not None:
                lines.insert(index+2, bstack11l111l1_opy_)
            lines.insert(1, bstack1ll1llll1_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack1ll1_opy_ (u"ࠥ࡭ࡳࡪࡥࡹࡡࡥࡷࡹࡧࡣ࡬࠰࡭ࡷࠧ௓")), bstack1ll1_opy_ (u"ࠫࡼ࠭௔")) as bstack1ll1ll_opy_:
              bstack1ll1ll_opy_.writelines(lines)
        CONFIG[bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧ௕")] = str(bstack1l1l1l11_opy_) + str(__version__)
        bstack111111l_opy_ = 0 if bstack1111ll_opy_ < 0 else bstack1111ll_opy_
        if bstack1l1ll1l_opy_ is True:
          bstack111111l_opy_ = int(threading.current_thread().getName())
        CONFIG[bstack1ll1_opy_ (u"ࠨࡵࡴࡧ࡚࠷ࡈࠨ௖")] = False
        bstack11l1l1l1_opy_ = bstack1llll11l1_opy_(CONFIG, bstack111111l_opy_)
        logger.debug(bstack11lll11_opy_.format(str(bstack11l1l1l1_opy_)))
        if CONFIG[bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫௗ")]:
          bstack11l1l1l_opy_(bstack11l1l1l1_opy_)
        if bstack1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ௘") in CONFIG and bstack1ll1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ௙") in CONFIG[bstack1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭௚")][bstack111111l_opy_]:
          bstack1ll111ll_opy_ = CONFIG[bstack1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ௛")][bstack111111l_opy_][bstack1ll1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ௜")]
        args.append(os.path.join(os.path.expanduser(bstack1ll1_opy_ (u"࠭ࡾࠨ௝")), bstack1ll1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ௞"), bstack1ll1_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪ௟")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack11l1l1l1_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack1ll1_opy_ (u"ࠤ࡬ࡲࡩ࡫ࡸࡠࡤࡶࡸࡦࡩ࡫࠯࡬ࡶࠦ௠"))
      return bstack1lll1l_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    logger.debug(bstack1llll111l_opy_ + str(e))
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack111ll1_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack1111111_opy_
    global bstack1111ll_opy_
    global bstack1ll111ll_opy_
    global bstack1l1ll1l_opy_
    global bstack1l1l1l11_opy_
    global bstack1lll1_opy_
    CONFIG[bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬ௡")] = str(bstack1l1l1l11_opy_) + str(__version__)
    bstack111111l_opy_ = 0 if bstack1111ll_opy_ < 0 else bstack1111ll_opy_
    if bstack1l1ll1l_opy_ is True:
      bstack111111l_opy_ = int(threading.current_thread().getName())
    CONFIG[bstack1ll1_opy_ (u"ࠦࡺࡹࡥࡘ࠵ࡆࠦ௢")] = False
    bstack11l1l1l1_opy_ = bstack1llll11l1_opy_(CONFIG, bstack111111l_opy_)
    logger.debug(bstack11lll11_opy_.format(str(bstack11l1l1l1_opy_)))
    if CONFIG[bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ௣")]:
      bstack11l1l1l_opy_(bstack11l1l1l1_opy_)
    if bstack1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ௤") in CONFIG and bstack1ll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ௥") in CONFIG[bstack1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ௦")][bstack111111l_opy_]:
      bstack1ll111ll_opy_ = CONFIG[bstack1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ௧")][bstack111111l_opy_][bstack1ll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ௨")]
    import urllib
    import json
    bstack111lll11_opy_ = bstack1ll1_opy_ (u"ࠫࡼࡹࡳ࠻࠱࠲ࡧࡩࡶ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠿ࡤࡣࡳࡷࡂ࠭௩") + urllib.parse.quote(json.dumps(bstack11l1l1l1_opy_))
    browser = self.connect(bstack111lll11_opy_)
    return browser
except Exception as e:
    logger.debug(bstack1llll111l_opy_ + str(e))
def bstack1ll1ll1l_opy_():
    try:
        from playwright._impl._browser_type import BrowserType
        BrowserType.launch = bstack111ll1_opy_
    except Exception as e:
        logger.debug(bstack1llll111l_opy_ + str(e))
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack111l11l1_opy_
    except Exception as e:
      logger.debug(bstack1llll111l_opy_ + str(e))
def bstack11llll_opy_(context, bstack11l11l1_opy_):
  try:
    context.page.evaluate(bstack1ll1_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨ௪"), bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠪ௫")+ json.dumps(bstack11l11l1_opy_) + bstack1ll1_opy_ (u"ࠢࡾࡿࠥ௬"))
  except Exception as e:
    logger.debug(bstack1ll1_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣࡿࢂࠨ௭"), e)
def bstack1ll1l1l_opy_(context, message, level):
  try:
    context.page.evaluate(bstack1ll1_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥ௮"), bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨ௯") + json.dumps(message) + bstack1ll1_opy_ (u"ࠫ࠱ࠨ࡬ࡦࡸࡨࡰࠧࡀࠧ௰") + json.dumps(level) + bstack1ll1_opy_ (u"ࠬࢃࡽࠨ௱"))
  except Exception as e:
    logger.debug(bstack1ll1_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡤࡲࡳࡵࡴࡢࡶ࡬ࡳࡳࠦࡻࡾࠤ௲"), e)
def bstack11ll1ll1_opy_(context, status, message = bstack1ll1_opy_ (u"ࠢࠣ௳")):
  try:
    if(status == bstack1ll1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ௴")):
      context.page.evaluate(bstack1ll1_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥ௵"), bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡵࡩࡦࡹ࡯࡯ࠤ࠽ࠫ௶") + json.dumps(bstack1ll1_opy_ (u"ࠦࡘࡩࡥ࡯ࡣࡵ࡭ࡴࠦࡦࡢ࡫࡯ࡩࡩࠦࡷࡪࡶ࡫࠾ࠥࠨ௷") + str(message)) + bstack1ll1_opy_ (u"ࠬ࠲ࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠩ௸") + json.dumps(status) + bstack1ll1_opy_ (u"ࠨࡽࡾࠤ௹"))
    else:
      context.page.evaluate(bstack1ll1_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ௺"), bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠩ௻") + json.dumps(status) + bstack1ll1_opy_ (u"ࠤࢀࢁࠧ௼"))
  except Exception as e:
    logger.debug(bstack1ll1_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶࠤࢀࢃࠢ௽"), e)
def bstack11llll1l_opy_(self, url):
  global bstack1l1lll_opy_
  try:
    bstack1lll111_opy_(url)
  except Exception as err:
    logger.debug(bstack1l1l1ll1_opy_.format(str(err)))
  try:
    bstack1l1lll_opy_(self, url)
  except Exception as e:
    try:
      bstack11llllll_opy_ = str(e)
      if any(err_msg in bstack11llllll_opy_ for err_msg in bstack1l1l1llll_opy_):
        bstack1lll111_opy_(url, True)
    except Exception as err:
      logger.debug(bstack1l1l1ll1_opy_.format(str(err)))
    raise e
def bstack11llll1_opy_(self, test):
  global CONFIG
  global bstack1111111_opy_
  global bstack111lll_opy_
  global bstack1ll111ll_opy_
  global bstack1ll1l11l_opy_
  try:
    if not bstack1111111_opy_:
      with open(os.path.join(os.path.expanduser(bstack1ll1_opy_ (u"ࠫࢃ࠭௾")), bstack1ll1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ௿"), bstack1ll1_opy_ (u"࠭࠮ࡴࡧࡶࡷ࡮ࡵ࡮ࡪࡦࡶ࠲ࡹࡾࡴࠨఀ"))) as f:
        bstack1ll1lllll_opy_ = json.loads(bstack1ll1_opy_ (u"ࠢࡼࠤఁ") + f.read().strip() + bstack1ll1_opy_ (u"ࠨࠤࡻࠦ࠿ࠦࠢࡺࠤࠪం") + bstack1ll1_opy_ (u"ࠤࢀࠦః"))
        bstack1111111_opy_ = bstack1ll1lllll_opy_[str(threading.get_ident())]
  except:
    pass
  if bstack1111111_opy_:
    try:
      data = {}
      bstack1l1lll1ll_opy_ = None
      if test:
        bstack1l1lll1ll_opy_ = str(test.data)
      if bstack1l1lll1ll_opy_ and not bstack1ll111ll_opy_:
        data[bstack1ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨఄ")] = bstack1l1lll1ll_opy_
      if bstack111lll_opy_:
        if bstack111lll_opy_.status == bstack1ll1_opy_ (u"ࠫࡕࡇࡓࡔࠩఅ"):
          data[bstack1ll1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬఆ")] = bstack1ll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ఇ")
        elif bstack111lll_opy_.status == bstack1ll1_opy_ (u"ࠧࡇࡃࡌࡐࠬఈ"):
          data[bstack1ll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨఉ")] = bstack1ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩఊ")
          if bstack111lll_opy_.message:
            data[bstack1ll1_opy_ (u"ࠪࡶࡪࡧࡳࡰࡰࠪఋ")] = str(bstack111lll_opy_.message)
      user = CONFIG[bstack1ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ఌ")]
      key = CONFIG[bstack1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ఍")]
      url = bstack1ll1_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡼࡿ࠽ࡿࢂࡆࡡࡱ࡫࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡡࡶࡶࡲࡱࡦࡺࡥ࠰ࡵࡨࡷࡸ࡯࡯࡯ࡵ࠲ࡿࢂ࠴ࡪࡴࡱࡱࠫఎ").format(user, key, bstack1111111_opy_)
      headers = {
        bstack1ll1_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡶࡼࡴࡪ࠭ఏ"): bstack1ll1_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫఐ"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers)
    except Exception as e:
      logger.error(bstack1l1l1ll_opy_.format(str(e)))
  bstack1ll1l11l_opy_(self, test)
def bstack1llll1lll_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack1111l11l_opy_
  bstack1111l11l_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack111lll_opy_
  bstack111lll_opy_ = self._test
def bstack1l111_opy_(outs_dir, options, tests_root_name, stats, copied_artifacts, outputfile=None):
  from pabot import pabot
  outputfile = outputfile or options.get(bstack1ll1_opy_ (u"ࠤࡲࡹࡹࡶࡵࡵࠤ఑"), bstack1ll1_opy_ (u"ࠥࡳࡺࡺࡰࡶࡶ࠱ࡼࡲࡲࠢఒ"))
  output_path = os.path.abspath(
    os.path.join(options.get(bstack1ll1_opy_ (u"ࠦࡴࡻࡴࡱࡷࡷࡨ࡮ࡸࠢఓ"), bstack1ll1_opy_ (u"ࠧ࠴ࠢఔ")), outputfile)
  )
  files = sorted(pabot.glob(os.path.join(pabot._glob_escape(outs_dir), bstack1ll1_opy_ (u"ࠨࠪ࠯ࡺࡰࡰࠧక"))))
  if not files:
    pabot._write(bstack1ll1_opy_ (u"ࠧࡘࡃࡕࡒ࠿ࠦࡎࡰࠢࡲࡹࡹࡶࡵࡵࠢࡩ࡭ࡱ࡫ࡳࠡ࡫ࡱࠤࠧࠫࡳࠣࠩఖ") % outs_dir, pabot.Color.YELLOW)
    return bstack1ll1_opy_ (u"ࠣࠤగ")
  def invalid_xml_callback():
    global _ABNORMAL_EXIT_HAPPENED
    _ABNORMAL_EXIT_HAPPENED = True
  resu = pabot.merge(
    files, options, tests_root_name, copied_artifacts, invalid_xml_callback
  )
  pabot._update_stats(resu, stats)
  resu.save(output_path)
  return output_path
def bstack11111ll1_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  from pabot import pabot
  from robot import __version__ as ROBOT_VERSION
  from robot import rebot
  if bstack1ll1_opy_ (u"ࠤࡳࡽࡹ࡮࡯࡯ࡲࡤࡸ࡭ࠨఘ") in options:
    del options[bstack1ll1_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࡳࡥࡹ࡮ࠢఙ")]
  if ROBOT_VERSION < bstack1ll1_opy_ (u"ࠦ࠹࠴࠰ࠣచ"):
    stats = {
      bstack1ll1_opy_ (u"ࠧࡩࡲࡪࡶ࡬ࡧࡦࡲࠢఛ"): {bstack1ll1_opy_ (u"ࠨࡴࡰࡶࡤࡰࠧజ"): 0, bstack1ll1_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠢఝ"): 0, bstack1ll1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣఞ"): 0},
      bstack1ll1_opy_ (u"ࠤࡤࡰࡱࠨట"): {bstack1ll1_opy_ (u"ࠥࡸࡴࡺࡡ࡭ࠤఠ"): 0, bstack1ll1_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦడ"): 0, bstack1ll1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧఢ"): 0},
    }
  else:
    stats = {
      bstack1ll1_opy_ (u"ࠨࡴࡰࡶࡤࡰࠧణ"): 0,
      bstack1ll1_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠢత"): 0,
      bstack1ll1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣథ"): 0,
      bstack1ll1_opy_ (u"ࠤࡶ࡯࡮ࡶࡰࡦࡦࠥద"): 0,
    }
  if pabot_args[bstack1ll1_opy_ (u"ࠥࡆࡘ࡚ࡁࡄࡍࡢࡔࡆࡘࡁࡍࡎࡈࡐࡤࡘࡕࡏࠤధ")]:
    outputs = []
    for index, _ in enumerate(pabot_args[bstack1ll1_opy_ (u"ࠦࡇ࡙ࡔࡂࡅࡎࡣࡕࡇࡒࡂࡎࡏࡉࡑࡥࡒࡖࡐࠥన")]):
      copied_artifacts = pabot._copy_output_artifacts(
        options, pabot_args[bstack1ll1_opy_ (u"ࠧࡧࡲࡵ࡫ࡩࡥࡨࡺࡳࠣ఩")], pabot_args[bstack1ll1_opy_ (u"ࠨࡡࡳࡶ࡬ࡪࡦࡩࡴࡴ࡫ࡱࡷࡺࡨࡦࡰ࡮ࡧࡩࡷࡹࠢప")]
      )
      outputs += [
        bstack1l111_opy_(
          os.path.join(outs_dir, str(index)+ bstack1ll1_opy_ (u"ࠢ࠰ࠤఫ")),
          options,
          tests_root_name,
          stats,
          copied_artifacts,
          outputfile=os.path.join(bstack1ll1_opy_ (u"ࠣࡲࡤࡦࡴࡺ࡟ࡳࡧࡶࡹࡱࡺࡳࠣబ"), bstack1ll1_opy_ (u"ࠤࡲࡹࡹࡶࡵࡵࠧࡶ࠲ࡽࡳ࡬ࠣభ") % index),
        )
      ]
    if bstack1ll1_opy_ (u"ࠥࡳࡺࡺࡰࡶࡶࠥమ") not in options:
      options[bstack1ll1_opy_ (u"ࠦࡴࡻࡴࡱࡷࡷࠦయ")] = bstack1ll1_opy_ (u"ࠧࡵࡵࡵࡲࡸࡸ࠳ࡾ࡭࡭ࠤర")
    pabot._write_stats(stats)
    return rebot(*outputs, **pabot._options_for_rebot(options, start_time_string, pabot._now()))
  else:
    return pabot._report_results(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack1l111l1l_opy_(self, ff_profile_dir):
  global bstack11l11ll1_opy_
  if not ff_profile_dir:
    return None
  return bstack11l11ll1_opy_(self, ff_profile_dir)
def bstack1ll11ll1l_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack111l1lll_opy_
  bstack1l1l1l1l1_opy_ = []
  if bstack1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩఱ") in CONFIG:
    bstack1l1l1l1l1_opy_ = CONFIG[bstack1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪల")]
  bstack1lll1l1_opy_ = len(suite_group) * len(pabot_args[bstack1ll1_opy_ (u"ࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡩ࡭ࡱ࡫ࡳࠣళ")] or [(bstack1ll1_opy_ (u"ࠤࠥఴ"), None)]) * len(bstack1l1l1l1l1_opy_)
  pabot_args[bstack1ll1_opy_ (u"ࠥࡆࡘ࡚ࡁࡄࡍࡢࡔࡆࡘࡁࡍࡎࡈࡐࡤࡘࡕࡏࠤవ")] = []
  for q in range(bstack1lll1l1_opy_):
    pabot_args[bstack1ll1_opy_ (u"ࠦࡇ࡙ࡔࡂࡅࡎࡣࡕࡇࡒࡂࡎࡏࡉࡑࡥࡒࡖࡐࠥశ")].append(str(q))
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack1ll1_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࠨష")],
      pabot_args[bstack1ll1_opy_ (u"ࠨࡶࡦࡴࡥࡳࡸ࡫ࠢస")],
      argfile,
      pabot_args.get(bstack1ll1_opy_ (u"ࠢࡩ࡫ࡹࡩࠧహ")),
      pabot_args[bstack1ll1_opy_ (u"ࠣࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠦ఺")],
      platform[0],
      bstack111l1lll_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack1ll1_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡪ࡮ࡲࡥࡴࠤ఻")] or [(bstack1ll1_opy_ (u"఼ࠥࠦ"), None)]
    for platform in enumerate(bstack1l1l1l1l1_opy_)
  ]
def bstack1l1111_opy_(self, datasources, outs_dir, options,
  execution_item, command, verbose, argfile,
  hive=None, processes=0,platform_index=0,bstack1l1lll111_opy_=bstack1ll1_opy_ (u"ࠫࠬఽ")):
  global bstack1111l1ll_opy_
  self.platform_index = platform_index
  self.bstack1111l1_opy_ = bstack1l1lll111_opy_
  bstack1111l1ll_opy_(self, datasources, outs_dir, options,
    execution_item, command, verbose, argfile, hive, processes)
def bstack1ll1ll1l1_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack1ll11111_opy_
  global bstack11l1l11l_opy_
  if not bstack1ll1_opy_ (u"ࠬࡼࡡࡳ࡫ࡤࡦࡱ࡫ࠧా") in item.options:
    item.options[bstack1ll1_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨి")] = []
  for v in item.options[bstack1ll1_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩీ")]:
    if bstack1ll1_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡑࡎࡄࡘࡋࡕࡒࡎࡋࡑࡈࡊ࡞ࠧు") in v:
      item.options[bstack1ll1_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫూ")].remove(v)
    if bstack1ll1_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡆࡐࡎࡇࡒࡈࡕࠪృ") in v:
      item.options[bstack1ll1_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭ౄ")].remove(v)
  item.options[bstack1ll1_opy_ (u"ࠬࡼࡡࡳ࡫ࡤࡦࡱ࡫ࠧ౅")].insert(0, bstack1ll1_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡖࡌࡂࡖࡉࡓࡗࡓࡉࡏࡆࡈ࡜࠿ࢁࡽࠨె").format(item.platform_index))
  item.options[bstack1ll1_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩే")].insert(0, bstack1ll1_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡅࡇࡉࡐࡔࡉࡁࡍࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖ࠿ࢁࡽࠨై").format(item.bstack1111l1_opy_))
  if bstack11l1l11l_opy_:
    item.options[bstack1ll1_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ౉")].insert(0, bstack1ll1_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡆࡐࡎࡇࡒࡈࡕ࠽ࡿࢂ࠭ొ").format(bstack11l1l11l_opy_))
  return bstack1ll11111_opy_(caller_id, datasources, is_last, item, outs_dir)
def bstack1111ll1l_opy_(command):
  global bstack11l1l11l_opy_
  if bstack11l1l11l_opy_:
    command[0] = command[0].replace(bstack1ll1_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪో"), bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠱ࡸࡪ࡫ࠡࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠢࠪౌ") + bstack11l1l11l_opy_, 1)
  else:
    command[0] = command[0].replace(bstack1ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸ్ࠬ"), bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠳ࡳࡥ࡭ࠣࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫ౎"), 1)
def bstack1lll1l1ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack1ll111_opy_
  bstack1111ll1l_opy_(command)
  return bstack1ll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
def bstack1l1111ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack1ll111_opy_
  bstack1111ll1l_opy_(command)
  return bstack1ll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
def bstack1ll1ll11l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack1ll111_opy_
  bstack1111ll1l_opy_(command)
  return bstack1ll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
def bstack1ll11l111_opy_(self, runner, quiet=False, capture=True):
  global bstack1ll1111_opy_
  bstack1l11llll_opy_ = bstack1ll1111_opy_(self, runner, quiet=False, capture=True)
  if self.exception:
    if not hasattr(runner, bstack1ll1_opy_ (u"ࠨࡧࡻࡧࡪࡶࡴࡪࡱࡱࡣࡦࡸࡲࠨ౏")):
      runner.exception_arr = []
    if not hasattr(runner, bstack1ll1_opy_ (u"ࠩࡨࡼࡨࡥࡴࡳࡣࡦࡩࡧࡧࡣ࡬ࡡࡤࡶࡷ࠭౐")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack1l11llll_opy_
def bstack1l1l111l1_opy_(self, name, context, *args):
  global bstack1l1ll11ll_opy_
  if name in [bstack1ll1_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࡢࡪࡪࡧࡴࡶࡴࡨࠫ౑"), bstack1ll1_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭౒")]:
    bstack1l1ll11ll_opy_(self, name, context, *args)
  if name == bstack1ll1_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࡤ࡬ࡥࡢࡶࡸࡶࡪ࠭౓"):
    try:
      bstack11l11l1_opy_ = str(self.feature.name)
      bstack11llll_opy_(context, bstack11l11l1_opy_)
      context.browser.execute_script(bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠣࠫ౔") + json.dumps(bstack11l11l1_opy_) + bstack1ll1_opy_ (u"ࠧࡾࡿౕࠪ"))
      self.driver_before_scenario = False
    except Exception as e:
      logger.debug(bstack1ll1_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫ࡴࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡱࡥࡲ࡫ࠠࡪࡰࠣࡦࡪ࡬࡯ࡳࡧࠣࡪࡪࡧࡴࡶࡴࡨ࠾ࠥࢁࡽࠨౖ").format(str(e)))
  if name == bstack1ll1_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫ౗"):
    try:
      if not hasattr(self, bstack1ll1_opy_ (u"ࠪࡨࡷ࡯ࡶࡦࡴࡢࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬౘ")):
        self.driver_before_scenario = True
      bstack1l11ll_opy_ = args[0].name
      bstack1l1lll11_opy_ = bstack11l11l1_opy_ = str(self.feature.name)
      bstack11l11l1_opy_ = bstack1l1lll11_opy_ + bstack1ll1_opy_ (u"ࠫࠥ࠳ࠠࠨౙ") + bstack1l11ll_opy_
      if self.driver_before_scenario:
        bstack11llll_opy_(context, bstack11l11l1_opy_)
        context.browser.execute_script(bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪౚ") + json.dumps(bstack11l11l1_opy_) + bstack1ll1_opy_ (u"࠭ࡽࡾࠩ౛"))
    except Exception as e:
      logger.debug(bstack1ll1_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡩ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡧࡪࡴࡡࡳ࡫ࡲ࠾ࠥࢁࡽࠨ౜").format(str(e)))
  if name == bstack1ll1_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠩౝ"):
    try:
      bstack1llll11_opy_ = args[0].status.name
      if str(bstack1llll11_opy_).lower() == bstack1ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ౞"):
        bstack11lll1l_opy_ = bstack1ll1_opy_ (u"ࠪࠫ౟")
        bstack1l1lllll1_opy_ = bstack1ll1_opy_ (u"ࠫࠬౠ")
        bstack1llllll1_opy_ = bstack1ll1_opy_ (u"ࠬ࠭ౡ")
        try:
          import traceback
          bstack11lll1l_opy_ = self.exception.__class__.__name__
          bstack1lll1l1l1_opy_ = traceback.format_tb(self.exc_traceback)
          bstack1l1lllll1_opy_ = bstack1ll1_opy_ (u"࠭ࠠࠨౢ").join(bstack1lll1l1l1_opy_)
          bstack1llllll1_opy_ = bstack1lll1l1l1_opy_[-1]
        except Exception as e:
          logger.debug(bstack1l1l1ll1l_opy_.format(str(e)))
        bstack11lll1l_opy_ += bstack1llllll1_opy_
        bstack1ll1l1l_opy_(context, json.dumps(str(args[0].name) + bstack1ll1_opy_ (u"ࠢࠡ࠯ࠣࡊࡦ࡯࡬ࡦࡦࠤࡠࡳࠨౣ") + str(bstack1l1lllll1_opy_)), bstack1ll1_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢ౤"))
        if self.driver_before_scenario:
          bstack11ll1ll1_opy_(context, bstack1ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤ౥"), bstack11lll1l_opy_)
        context.browser.execute_script(bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨ౦") + json.dumps(str(args[0].name) + bstack1ll1_opy_ (u"ࠦࠥ࠳ࠠࡇࡣ࡬ࡰࡪࡪࠡ࡝ࡰࠥ౧") + str(bstack1l1lllll1_opy_)) + bstack1ll1_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥࡩࡷࡸ࡯ࡳࠤࢀࢁࠬ౨"))
        if self.driver_before_scenario:
          context.browser.execute_script(bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡹࡴࡢࡶࡸࡷࠧࡀࠢࡧࡣ࡬ࡰࡪࡪࠢ࠭ࠢࠥࡶࡪࡧࡳࡰࡰࠥ࠾ࠥ࠭౩") + json.dumps(bstack1ll1_opy_ (u"ࠢࡔࡥࡨࡲࡦࡸࡩࡰࠢࡩࡥ࡮ࡲࡥࡥࠢࡺ࡭ࡹ࡮࠺ࠡ࡞ࡱࠦ౪") + str(bstack11lll1l_opy_)) + bstack1ll1_opy_ (u"ࠨࡿࢀࠫ౫"))
      else:
        bstack1ll1l1l_opy_(context, bstack1ll1_opy_ (u"ࠤࡓࡥࡸࡹࡥࡥࠣࠥ౬"), bstack1ll1_opy_ (u"ࠥ࡭ࡳ࡬࡯ࠣ౭"))
        if self.driver_before_scenario:
          bstack11ll1ll1_opy_(context, bstack1ll1_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦ౮"))
        context.browser.execute_script(bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪ౯") + json.dumps(str(args[0].name) + bstack1ll1_opy_ (u"ࠨࠠ࠮ࠢࡓࡥࡸࡹࡥࡥࠣࠥ౰")) + bstack1ll1_opy_ (u"ࠧ࠭ࠢࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠤࠧ࡯࡮ࡧࡱࠥࢁࢂ࠭౱"))
        if self.driver_before_scenario:
          context.browser.execute_script(bstack1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠤࡳࡥࡸࡹࡥࡥࠤࢀࢁࠬ౲"))
    except Exception as e:
      logger.debug(bstack1ll1_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡳࡡࡳ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶࠤ࡮ࡴࠠࡢࡨࡷࡩࡷࠦࡦࡦࡣࡷࡹࡷ࡫࠺ࠡࡽࢀࠫ౳").format(str(e)))
  if name == bstack1ll1_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡩࡩࡦࡺࡵࡳࡧࠪ౴"):
    try:
      if context.failed is True:
        bstack11l1l1_opy_ = []
        bstack1ll11lll1_opy_ = []
        bstack111111_opy_ = []
        bstack111ll1l_opy_ = bstack1ll1_opy_ (u"ࠫࠬ౵")
        try:
          import traceback
          for exc in self.exception_arr:
            bstack11l1l1_opy_.append(exc.__class__.__name__)
          for exc_tb in self.exc_traceback_arr:
            bstack1lll1l1l1_opy_ = traceback.format_tb(exc_tb)
            bstack1llll111_opy_ = bstack1ll1_opy_ (u"ࠬࠦࠧ౶").join(bstack1lll1l1l1_opy_)
            bstack1ll11lll1_opy_.append(bstack1llll111_opy_)
            bstack111111_opy_.append(bstack1lll1l1l1_opy_[-1])
        except Exception as e:
          logger.debug(bstack1l1l1ll1l_opy_.format(str(e)))
        bstack11lll1l_opy_ = bstack1ll1_opy_ (u"࠭ࠧ౷")
        for i in range(len(bstack11l1l1_opy_)):
          bstack11lll1l_opy_ += bstack11l1l1_opy_[i] + bstack111111_opy_[i] + bstack1ll1_opy_ (u"ࠧ࡝ࡰࠪ౸")
        bstack111ll1l_opy_ = bstack1ll1_opy_ (u"ࠨࠢࠪ౹").join(bstack1ll11lll1_opy_)
        if not self.driver_before_scenario:
          bstack1ll1l1l_opy_(context, bstack111ll1l_opy_, bstack1ll1_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣ౺"))
          bstack11ll1ll1_opy_(context, bstack1ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥ౻"), bstack11lll1l_opy_)
          context.browser.execute_script(bstack1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩ౼") + json.dumps(bstack111ll1l_opy_) + bstack1ll1_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥࡩࡷࡸ࡯ࡳࠤࢀࢁࠬ౽"))
          context.browser.execute_script(bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡹࡴࡢࡶࡸࡷࠧࡀࠢࡧࡣ࡬ࡰࡪࡪࠢ࠭ࠢࠥࡶࡪࡧࡳࡰࡰࠥ࠾ࠥ࠭౾") + json.dumps(bstack1ll1_opy_ (u"ࠢࡔࡱࡰࡩࠥࡹࡣࡦࡰࡤࡶ࡮ࡵࡳࠡࡨࡤ࡭ࡱ࡫ࡤ࠻ࠢ࡟ࡲࠧ౿") + str(bstack11lll1l_opy_)) + bstack1ll1_opy_ (u"ࠨࡿࢀࠫಀ"))
      else:
        if not self.driver_before_scenario:
          bstack1ll1l1l_opy_(context, bstack1ll1_opy_ (u"ࠤࡉࡩࡦࡺࡵࡳࡧ࠽ࠤࠧಁ") + str(self.feature.name) + bstack1ll1_opy_ (u"ࠥࠤࡵࡧࡳࡴࡧࡧࠥࠧಂ"), bstack1ll1_opy_ (u"ࠦ࡮ࡴࡦࡰࠤಃ"))
          bstack11ll1ll1_opy_(context, bstack1ll1_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧ಄"))
          context.browser.execute_script(bstack1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫಅ") + json.dumps(bstack1ll1_opy_ (u"ࠢࡇࡧࡤࡸࡺࡸࡥ࠻ࠢࠥಆ") + str(self.feature.name) + bstack1ll1_opy_ (u"ࠣࠢࡳࡥࡸࡹࡥࡥࠣࠥಇ")) + bstack1ll1_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡪࡰࡩࡳࠧࢃࡽࠨಈ"))
          context.browser.execute_script(bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡶࡸࡦࡺࡵࡴࠤ࠽ࠦࡵࡧࡳࡴࡧࡧࠦࢂࢃࠧಉ"))
    except Exception as e:
      logger.debug(bstack1ll1_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠ࡮ࡣࡵ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡳࡵࡣࡷࡹࡸࠦࡩ࡯ࠢࡤࡪࡹ࡫ࡲࠡࡨࡨࡥࡹࡻࡲࡦ࠼ࠣࡿࢂ࠭ಊ").format(str(e)))
  if name in [bstack1ll1_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣ࡫࡫ࡡࡵࡷࡵࡩࠬಋ"), bstack1ll1_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠧಌ")]:
    bstack1l1ll11ll_opy_(self, name, context, *args)
    if (name == bstack1ll1_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠨ಍") and self.driver_before_scenario) or (name == bstack1ll1_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡧࡧࡤࡸࡺࡸࡥࠨಎ") and not self.driver_before_scenario):
      try:
        context.browser.quit()
      except Exception:
        pass
def bstack1lllllll1_opy_(config, startdir):
  return bstack1ll1_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿ࠵ࢃࠢಏ").format(bstack1ll1_opy_ (u"ࠥࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠤಐ"))
class Notset:
  def __repr__(self):
    return bstack1ll1_opy_ (u"ࠦࡁࡔࡏࡕࡕࡈࡘࡃࠨ಑")
notset = Notset()
def bstack1ll1ll11_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack11ll1l1l_opy_
  if str(name).lower() == bstack1ll1_opy_ (u"ࠬࡪࡲࡪࡸࡨࡶࠬಒ"):
    return bstack1ll1_opy_ (u"ࠨࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠧಓ")
  else:
    return bstack11ll1l1l_opy_(self, name, default, skip)
def bstack111l111l_opy_(bstack11l1l11_opy_):
  global bstack1l1l1l11_opy_
  bstack1l1l1l11_opy_ = bstack11l1l11_opy_
  logger.info(bstack1l1l1l1ll_opy_.format(bstack1l1l1l11_opy_.split(bstack1ll1_opy_ (u"ࠧ࠮ࠩಔ"))[0]))
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
  except Exception as e:
    logger.warn(bstack11l11_opy_ + str(e))
  Service.start = bstack1lll11111_opy_
  Service.stop = bstack1llll1l11_opy_
  webdriver.Remote.__init__ = bstack1llll1111_opy_
  webdriver.Remote.get = bstack11llll1l_opy_
  WebDriver.close = bstack111l11ll_opy_
  bstack1ll1ll1l_opy_()
  if bstack1ll1l1ll_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      RemoteConnection._get_proxy_url = bstack111l1ll1_opy_
    except Exception as e:
      logger.error(bstack1l11ll1ll_opy_.format(str(e)))
  if (bstack1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧಕ") in str(bstack11l1l11_opy_).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1l111l1l_opy_
      except Exception as e:
        logger.warn(bstack1llll1ll1_opy_ + str(e))
    except Exception as e:
      bstack11l1_opy_(e, bstack1llll1ll1_opy_)
    Output.end_test = bstack11llll1_opy_
    TestStatus.__init__ = bstack1llll1lll_opy_
    QueueItem.__init__ = bstack1l1111_opy_
    pabot._create_items = bstack1ll11ll1l_opy_
    try:
      from pabot import __version__ as bstack11l11111_opy_
      if version.parse(bstack11l11111_opy_) >= version.parse(bstack1ll1_opy_ (u"ࠩ࠵࠲࠶࠻࠮࠱ࠩಖ")):
        pabot._run = bstack1ll1ll11l_opy_
      elif version.parse(bstack11l11111_opy_) >= version.parse(bstack1ll1_opy_ (u"ࠪ࠶࠳࠷࠳࠯࠲ࠪಗ")):
        pabot._run = bstack1l1111ll_opy_
      else:
        pabot._run = bstack1lll1l1ll_opy_
    except Exception as e:
      pabot._run = bstack1lll1l1ll_opy_
    pabot._create_command_for_execution = bstack1ll1ll1l1_opy_
    pabot._report_results = bstack11111ll1_opy_
  if bstack1ll1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫಘ") in str(bstack11l1l11_opy_).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack11l1_opy_(e, bstack1l111ll_opy_)
    Runner.run_hook = bstack1l1l111l1_opy_
    Step.run = bstack1ll11l111_opy_
  if bstack1ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬಙ") in str(bstack11l1l11_opy_).lower():
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
    except Exception as e:
      bstack11l1_opy_(e, bstack1lll11ll1_opy_)
    pytest_selenium.pytest_report_header = bstack1lllllll1_opy_
    Config.getoption = bstack1ll1ll11_opy_
def bstack1lll1l11l_opy_():
  global CONFIG
  if bstack1ll1_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭ಚ") in CONFIG and int(CONFIG[bstack1ll1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧಛ")]) > 1:
    logger.warn(bstack11ll1l_opy_)
def bstack1l1ll11l1_opy_(bstack1l1l11l_opy_, index):
  bstack111l111l_opy_(bstack1lllll111_opy_)
  exec(open(bstack1l1l11l_opy_).read())
def bstack1l11l1ll_opy_(arg):
  global CONFIG
  bstack111l111l_opy_(bstack1l11l1ll1_opy_)
  os.environ[bstack1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡖࡕࡈࡖࡓࡇࡍࡆࠩಜ")] = CONFIG[bstack1ll1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫಝ")]
  os.environ[bstack1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄࡇࡈࡋࡓࡔࡡࡎࡉ࡞࠭ಞ")] = CONFIG[bstack1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧಟ")]
  from _pytest.config import main as bstack1lll11ll_opy_
  bstack1lll11ll_opy_(arg)
def bstack1l1111l_opy_(arg):
  bstack111l111l_opy_(bstack1lllll11_opy_)
  from behave.__main__ import main as bstack1111lll_opy_
  bstack1111lll_opy_(arg)
def bstack11ll111_opy_():
  logger.info(bstack1111llll_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack1ll1_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫಠ"), help=bstack1ll1_opy_ (u"࠭ࡇࡦࡰࡨࡶࡦࡺࡥࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡤࡱࡱࡪ࡮࡭ࠧಡ"))
  parser.add_argument(bstack1ll1_opy_ (u"ࠧ࠮ࡷࠪಢ"), bstack1ll1_opy_ (u"ࠨ࠯࠰ࡹࡸ࡫ࡲ࡯ࡣࡰࡩࠬಣ"), help=bstack1ll1_opy_ (u"ࠩ࡜ࡳࡺࡸࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡵࡴࡧࡵࡲࡦࡳࡥࠨತ"))
  parser.add_argument(bstack1ll1_opy_ (u"ࠪ࠱ࡰ࠭ಥ"), bstack1ll1_opy_ (u"ࠫ࠲࠳࡫ࡦࡻࠪದ"), help=bstack1ll1_opy_ (u"ࠬ࡟࡯ࡶࡴࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡤࡧࡨ࡫ࡳࡴࠢ࡮ࡩࡾ࠭ಧ"))
  parser.add_argument(bstack1ll1_opy_ (u"࠭࠭ࡧࠩನ"), bstack1ll1_opy_ (u"ࠧ࠮࠯ࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ಩"), help=bstack1ll1_opy_ (u"ࠨ࡛ࡲࡹࡷࠦࡴࡦࡵࡷࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧಪ"))
  bstack1l1ll11_opy_ = parser.parse_args()
  try:
    bstack1l11lll11_opy_ = bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡩࡨࡲࡪࡸࡩࡤ࠰ࡼࡱࡱ࠴ࡳࡢ࡯ࡳࡰࡪ࠭ಫ")
    if bstack1l1ll11_opy_.framework and bstack1l1ll11_opy_.framework not in (bstack1ll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪಬ"), bstack1ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱ࠷ࠬಭ")):
      bstack1l11lll11_opy_ = bstack1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࠮ࡺ࡯࡯࠲ࡸࡧ࡭ࡱ࡮ࡨࠫಮ")
    bstack1l1l1l1l_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l11lll11_opy_)
    bstack1l11111l_opy_ = open(bstack1l1l1l1l_opy_, bstack1ll1_opy_ (u"࠭ࡲࠨಯ"))
    bstack111lll1_opy_ = bstack1l11111l_opy_.read()
    bstack1l11111l_opy_.close()
    if bstack1l1ll11_opy_.username:
      bstack111lll1_opy_ = bstack111lll1_opy_.replace(bstack1ll1_opy_ (u"࡚ࠧࡑࡘࡖࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠧರ"), bstack1l1ll11_opy_.username)
    if bstack1l1ll11_opy_.key:
      bstack111lll1_opy_ = bstack111lll1_opy_.replace(bstack1ll1_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪಱ"), bstack1l1ll11_opy_.key)
    if bstack1l1ll11_opy_.framework:
      bstack111lll1_opy_ = bstack111lll1_opy_.replace(bstack1ll1_opy_ (u"ࠩ࡜ࡓ࡚ࡘ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪಲ"), bstack1l1ll11_opy_.framework)
    file_name = bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡼࡱࡱ࠭ಳ")
    file_path = os.path.abspath(file_name)
    bstack11111_opy_ = open(file_path, bstack1ll1_opy_ (u"ࠫࡼ࠭಴"))
    bstack11111_opy_.write(bstack111lll1_opy_)
    bstack11111_opy_.close()
    logger.info(bstack11111ll_opy_)
    try:
      os.environ[bstack1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧವ")] = bstack1l1ll11_opy_.framework if bstack1l1ll11_opy_.framework != None else bstack1ll1_opy_ (u"ࠨࠢಶ")
      config = yaml.safe_load(bstack111lll1_opy_)
      config[bstack1ll1_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧಷ")] = bstack1ll1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠮ࡵࡨࡸࡺࡶࠧಸ")
      bstack1l11l1l_opy_(bstack1l11l1l1_opy_, config)
    except Exception as e:
      logger.debug(bstack11ll11l_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack1l111111_opy_.format(str(e)))
def bstack1l11l1l_opy_(bstack111l1l11_opy_, config, bstack111l1ll_opy_ = {}):
  global bstack111lllll_opy_
  if not config:
    return
  bstack1llllll11_opy_ = bstack11ll111l_opy_ if not bstack111lllll_opy_ else ( bstack1l1l1l111_opy_ if bstack1ll1_opy_ (u"ࠩࡤࡴࡵ࠭ಹ") in config else bstack1lllllll_opy_ )
  data = {
    bstack1ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ಺"): config[bstack1ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭಻")],
    bstack1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ಼"): config[bstack1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩಽ")],
    bstack1ll1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫಾ"): bstack111l1l11_opy_,
    bstack1ll1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡱࡴࡲࡴࡪࡸࡴࡪࡧࡶࠫಿ"): {
      bstack1ll1_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧೀ"): str(config[bstack1ll1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪು")]) if bstack1ll1_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫೂ") in config else bstack1ll1_opy_ (u"ࠧࡻ࡮࡬ࡰࡲࡻࡳࠨೃ"),
      bstack1ll1_opy_ (u"࠭ࡲࡦࡨࡨࡶࡷ࡫ࡲࠨೄ"): bstack1111ll11_opy_(os.getenv(bstack1ll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠤ೅"), bstack1ll1_opy_ (u"ࠣࠤೆ"))),
      bstack1ll1_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨࠫೇ"): bstack1ll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪೈ"),
      bstack1ll1_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࠬ೉"): bstack1llllll11_opy_,
      bstack1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨೊ"): config[bstack1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩೋ")]if config[bstack1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪೌ")] else bstack1ll1_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࠤ್"),
      bstack1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ೎"): str(config[bstack1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ೏")]) if bstack1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭೐") in config else bstack1ll1_opy_ (u"ࠧࡻ࡮࡬ࡰࡲࡻࡳࠨ೑"),
      bstack1ll1_opy_ (u"࠭࡯ࡴࠩ೒"): sys.platform,
      bstack1ll1_opy_ (u"ࠧࡩࡱࡶࡸࡳࡧ࡭ࡦࠩ೓"): socket.gethostname()
    }
  }
  update(data[bstack1ll1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡱࡴࡲࡴࡪࡸࡴࡪࡧࡶࠫ೔")], bstack111l1ll_opy_)
  try:
    response = bstack1l11lll1_opy_(bstack1ll1_opy_ (u"ࠩࡓࡓࡘ࡚ࠧೕ"), bstack1llll11l_opy_, data, config)
    if response:
      logger.debug(bstack11ll11_opy_.format(bstack111l1l11_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack1l1l11111_opy_.format(str(e)))
def bstack1l11lll1_opy_(type, url, data, config):
  bstack1lll1lll1_opy_ = bstack1l1l11_opy_.format(url)
  proxy = bstack111l1111_opy_(config)
  proxies = {}
  response = {}
  if config.get(bstack1ll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭ೖ")):
    proxies = {
      bstack1ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪ೗"): proxy
    }
  if config.get(bstack1ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩ೘")):
    proxies = {
      bstack1ll1_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬ೙"): proxy
    }
  if type == bstack1ll1_opy_ (u"ࠧࡑࡑࡖࡘࠬ೚"):
    response = requests.post(bstack1lll1lll1_opy_, json=data,
                    headers={bstack1ll1_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧ೛"): bstack1ll1_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬ೜")}, auth=(config[bstack1ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬೝ")], config[bstack1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧೞ")]), proxies=proxies)
  return response
def bstack1111ll11_opy_(framework):
  return bstack1ll1_opy_ (u"ࠧࢁࡽ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࡻࡾࠤ೟").format(str(framework), __version__) if framework else bstack1ll1_opy_ (u"ࠨࡰࡺࡶ࡫ࡳࡳࡧࡧࡦࡰࡷ࠳ࢀࢃࠢೠ").format(__version__)
def bstack1ll11l1ll_opy_():
  global CONFIG
  if bool(CONFIG):
    return
  bstack1lll1ll11_opy_()
  logger.debug(bstack1l1ll1_opy_.format(str(CONFIG)))
  bstack11l111ll_opy_()
  sys.excepthook = bstack11l11l1l_opy_
  atexit.register(bstack1l1l11l1l_opy_)
  signal.signal(signal.SIGINT, bstack1l1llll11_opy_)
  signal.signal(signal.SIGTERM, bstack1l1llll11_opy_)
def bstack11l11l1l_opy_(exctype, value, traceback):
  global bstack111l_opy_
  try:
    for driver in bstack111l_opy_:
      driver.execute_script(
        bstack1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ࠮ࠣࠦࡷ࡫ࡡࡴࡱࡱࠦ࠿ࠦࠧೡ") + json.dumps(bstack1ll1_opy_ (u"ࠣࡕࡨࡷࡸ࡯࡯࡯ࠢࡩࡥ࡮ࡲࡥࡥࠢࡺ࡭ࡹ࡮࠺ࠡ࡞ࡱࠦೢ") + str(value)) + bstack1ll1_opy_ (u"ࠩࢀࢁࠬೣ"))
  except Exception:
    pass
  bstack11111l1_opy_(value)
  sys.__excepthook__(exctype, value, traceback)
def bstack11111l1_opy_(message = bstack1ll1_opy_ (u"ࠪࠫ೤")):
  global CONFIG
  try:
    if message:
      bstack111l1ll_opy_ = {
        bstack1ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ೥"): str(message)
      }
      bstack1l11l1l_opy_(bstack1lll1l111_opy_, CONFIG, bstack111l1ll_opy_)
    else:
      bstack1l11l1l_opy_(bstack1lll1l111_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack1l1lll11l_opy_.format(str(e)))
def bstack11l1lll_opy_(bstack11lll1l1_opy_, size):
  bstack1ll111ll1_opy_ = []
  while len(bstack11lll1l1_opy_) > size:
    bstack1l1111l1_opy_ = bstack11lll1l1_opy_[:size]
    bstack1ll111ll1_opy_.append(bstack1l1111l1_opy_)
    bstack11lll1l1_opy_   = bstack11lll1l1_opy_[size:]
  bstack1ll111ll1_opy_.append(bstack11lll1l1_opy_)
  return bstack1ll111ll1_opy_
def run_on_browserstack():
  if len(sys.argv) <= 1:
    logger.critical(bstack1lll1lll_opy_)
    return
  if sys.argv[1] == bstack1ll1_opy_ (u"ࠬ࠳࠭ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ೦")  or sys.argv[1] == bstack1ll1_opy_ (u"࠭࠭ࡷࠩ೧"):
    logger.info(bstack1ll1_opy_ (u"ࠧࡃࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡐࡺࡶ࡫ࡳࡳࠦࡓࡅࡍࠣࡺࢀࢃࠧ೨").format(__version__))
    return
  if sys.argv[1] == bstack1ll1_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧ೩"):
    bstack11ll111_opy_()
    return
  args = sys.argv
  bstack1ll11l1ll_opy_()
  global CONFIG
  global bstack1llll1_opy_
  global bstack1l1ll1l_opy_
  global bstack1111ll_opy_
  global bstack111l1lll_opy_
  global bstack11l1l11l_opy_
  bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"ࠩࠪ೪")
  if args[1] == bstack1ll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ೫") or args[1] == bstack1ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱ࠷ࠬ೬"):
    bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ೭")
    args = args[2:]
  elif args[1] == bstack1ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ೮"):
    bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭೯")
    args = args[2:]
  elif args[1] == bstack1ll1_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧ೰"):
    bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨೱ")
    args = args[2:]
  elif args[1] == bstack1ll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫೲ"):
    bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬೳ")
    args = args[2:]
  elif args[1] == bstack1ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ೴"):
    bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭೵")
    args = args[2:]
  elif args[1] == bstack1ll1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧ೶"):
    bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨ೷")
    args = args[2:]
  else:
    if not bstack1ll1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ೸") in CONFIG or str(CONFIG[bstack1ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭೹")]).lower() in [bstack1ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫ೺"), bstack1ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠸࠭೻")]:
      bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭೼")
      args = args[1:]
    elif str(CONFIG[bstack1ll1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ೽")]).lower() == bstack1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ೾"):
      bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ೿")
      args = args[1:]
    elif str(CONFIG[bstack1ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ഀ")]).lower() == bstack1ll1_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪഁ"):
      bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫം")
      args = args[1:]
    elif str(CONFIG[bstack1ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩഃ")]).lower() == bstack1ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧഄ"):
      bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨഅ")
      args = args[1:]
    elif str(CONFIG[bstack1ll1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬആ")]).lower() == bstack1ll1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪഇ"):
      bstack1l1ll1lll_opy_ = bstack1ll1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫഈ")
      args = args[1:]
    else:
      os.environ[bstack1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧഉ")] = bstack1l1ll1lll_opy_
      bstack1ll1lll_opy_(bstack1111l1l1_opy_)
  global bstack1lll1l_opy_
  try:
    os.environ[bstack1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨഊ")] = bstack1l1ll1lll_opy_
    bstack1l11l1l_opy_(bstack1l1llll1l_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack1l1lll11l_opy_.format(str(e)))
  global bstack1lll1_opy_
  global bstack1ll1l11l_opy_
  global bstack1111l11l_opy_
  global bstack11l11ll1_opy_
  global bstack1ll111_opy_
  global bstack1111l1ll_opy_
  global bstack1ll11111_opy_
  global bstack1ll1l1ll1_opy_
  global bstack1l1ll11ll_opy_
  global bstack1ll1111_opy_
  global bstack1l1lll_opy_
  global bstack111lll1l_opy_
  global bstack11ll1l1l_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
  except Exception as e:
    logger.warn(bstack11l11_opy_ + str(e))
  bstack1lll1_opy_ = webdriver.Remote.__init__
  bstack1ll1l1ll1_opy_ = WebDriver.close
  try:
    import Browser
    from subprocess import Popen
    bstack1lll1l_opy_ = Popen.__init__
  except Exception as e:
    logger.debug(bstack1llll111l_opy_ + str(e))
  bstack1l1lll_opy_ = WebDriver.get
  if bstack11l1l1ll_opy_():
    if bstack1ll1llll_opy_() < version.parse(bstack1lllll1l_opy_):
      logger.error(bstack11lllll_opy_.format(bstack1ll1llll_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        bstack111lll1l_opy_ = RemoteConnection._get_proxy_url
      except Exception as e:
        logger.error(bstack1l11ll1ll_opy_.format(str(e)))
  if (bstack1l1ll1lll_opy_ in [bstack1ll1_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭ഋ"), bstack1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧഌ"), bstack1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪ഍")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1l111l1l_opy_
      except Exception as e:
        logger.warn(bstack1llll1ll1_opy_ + str(e))
    except Exception as e:
      bstack11l1_opy_(e, bstack1llll1ll1_opy_)
    bstack1ll1l11l_opy_ = Output.end_test
    bstack1111l11l_opy_ = TestStatus.__init__
    bstack1ll111_opy_ = pabot._run
    bstack1111l1ll_opy_ = QueueItem.__init__
    bstack1ll11111_opy_ = pabot._create_command_for_execution
  if bstack1l1ll1lll_opy_ == bstack1ll1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪഎ"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack11l1_opy_(e, bstack1l111ll_opy_)
    bstack1l1ll11ll_opy_ = Runner.run_hook
    bstack1ll1111_opy_ = Step.run
  if bstack1l1ll1lll_opy_ == bstack1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫഏ"):
    try:
      from _pytest.config import Config
    except Exception as e:
      bstack11l1_opy_(e, bstack1lll11ll1_opy_)
    bstack11ll1l1l_opy_ = Config.getoption
  if bstack1l1ll1lll_opy_ == bstack1ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬഐ"):
    bstack1l1l1111l_opy_()
    bstack1lll1l11l_opy_()
    if bstack1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ഑") in CONFIG:
      bstack1l1ll1l_opy_ = True
      bstack1l1l1111_opy_ = []
      for index, platform in enumerate(CONFIG[bstack1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪഒ")]):
        bstack1l1l1111_opy_.append(bstack11lll1ll_opy_(name=str(index),
                                      target=bstack1l1ll11l1_opy_, args=(args[0], index)))
      for t in bstack1l1l1111_opy_:
        t.start()
      for t in bstack1l1l1111_opy_:
        t.join()
    else:
      bstack111l111l_opy_(bstack1lllll111_opy_)
      exec(open(args[0]).read())
  elif bstack1l1ll1lll_opy_ == bstack1ll1_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧഓ") or bstack1l1ll1lll_opy_ == bstack1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨഔ"):
    try:
      from pabot import pabot
    except Exception as e:
      bstack11l1_opy_(e, bstack1llll1ll1_opy_)
    bstack1l1l1111l_opy_()
    bstack111l111l_opy_(bstack1l1l1l_opy_)
    if bstack1ll1_opy_ (u"ࠪ࠱࠲ࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨക") in args:
      i = args.index(bstack1ll1_opy_ (u"ࠫ࠲࠳ࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩഖ"))
      args.pop(i)
      args.pop(i)
    args.insert(0, str(bstack1llll1_opy_))
    args.insert(0, str(bstack1ll1_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪഗ")))
    pabot.main(args)
  elif bstack1l1ll1lll_opy_ == bstack1ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠧഘ"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack11l1_opy_(e, bstack1llll1ll1_opy_)
    for a in args:
      if bstack1ll1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡐࡍࡃࡗࡊࡔࡘࡍࡊࡐࡇࡉ࡝࠭ങ") in a:
        bstack1111ll_opy_ = int(a.split(bstack1ll1_opy_ (u"ࠨ࠼ࠪച"))[1])
      if bstack1ll1_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡆࡈࡊࡑࡕࡃࡂࡎࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭ഛ") in a:
        bstack111l1lll_opy_ = str(a.split(bstack1ll1_opy_ (u"ࠪ࠾ࠬജ"))[1])
      if bstack1ll1_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡇࡑࡏࡁࡓࡉࡖࠫഝ") in a:
        bstack11l1l11l_opy_ = str(a.split(bstack1ll1_opy_ (u"ࠬࡀࠧഞ"))[1])
    bstack111l111l_opy_(bstack1l1l1l_opy_)
    run_cli(args)
  elif bstack1l1ll1lll_opy_ == bstack1ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ട"):
    try:
      from _pytest.config import _prepareconfig
      from _pytest.config import Config
      import importlib
      bstack1ll1111l_opy_ = importlib.find_loader(bstack1ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩഠ"))
      if bstack1ll1111l_opy_ is None:
        bstack11l1_opy_(e, bstack1lll11ll1_opy_)
    except Exception as e:
      bstack11l1_opy_(e, bstack1lll11ll1_opy_)
    bstack1l1l1111l_opy_()
    try:
      if bstack1ll1_opy_ (u"ࠨ࠯࠰ࡨࡷ࡯ࡶࡦࡴࠪഡ") in args:
        i = args.index(bstack1ll1_opy_ (u"ࠩ࠰࠱ࡩࡸࡩࡷࡧࡵࠫഢ"))
        args.pop(i+1)
        args.pop(i)
      if bstack1ll1_opy_ (u"ࠪ࠱࠲ࡶ࡬ࡶࡩ࡬ࡲࡸ࠭ണ") in args:
        i = args.index(bstack1ll1_opy_ (u"ࠫ࠲࠳ࡰ࡭ࡷࡪ࡭ࡳࡹࠧത"))
        args.pop(i+1)
        args.pop(i)
      if bstack1ll1_opy_ (u"ࠬ࠳ࡰࠨഥ") in args:
        i = args.index(bstack1ll1_opy_ (u"࠭࠭ࡱࠩദ"))
        args.pop(i+1)
        args.pop(i)
      if bstack1ll1_opy_ (u"ࠧ࠮࠯ࡱࡹࡲࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨധ") in args:
        i = args.index(bstack1ll1_opy_ (u"ࠨ࠯࠰ࡲࡺࡳࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩന"))
        args.pop(i+1)
        args.pop(i)
      if bstack1ll1_opy_ (u"ࠩ࠰ࡲࠬഩ") in args:
        i = args.index(bstack1ll1_opy_ (u"ࠪ࠱ࡳ࠭പ"))
        args.pop(i+1)
        args.pop(i)
    except Exception as exc:
      logger.error(str(exc))
    config = _prepareconfig(args)
    bstack1l1ll11l_opy_ = config.args
    bstack111l1l_opy_ = config.invocation_params.args
    bstack111l1l_opy_ = list(bstack111l1l_opy_)
    bstack1l1lll1l1_opy_ = []
    for arg in bstack111l1l_opy_:
      for spec in bstack1l1ll11l_opy_:
        if os.path.normpath(arg) != os.path.normpath(spec):
          bstack1l1lll1l1_opy_.append(arg)
    import platform as pf
    if pf.system().lower() == bstack1ll1_opy_ (u"ࠫࡼ࡯࡮ࡥࡱࡺࡷࠬഫ"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1l1ll11l_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11lll_opy_)))
                    for bstack11lll_opy_ in bstack1l1ll11l_opy_]
    bstack1l1lll1l1_opy_.append(bstack1ll1_opy_ (u"ࠬ࠳ࡰࠨബ"))
    bstack1l1lll1l1_opy_.append(bstack1ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡵࡲࡵࡨ࡫ࡱࠫഭ"))
    bstack1l1lll1l1_opy_.append(bstack1ll1_opy_ (u"ࠧ࠮࠯ࡧࡶ࡮ࡼࡥࡳࠩമ"))
    bstack1l1lll1l1_opy_.append(bstack1ll1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࠨയ"))
    bstack1lllll11l_opy_ = []
    for spec in bstack1l1ll11l_opy_:
      bstack111l11_opy_ = []
      bstack111l11_opy_.append(spec)
      bstack111l11_opy_ += bstack1l1lll1l1_opy_
      bstack1lllll11l_opy_.append(bstack111l11_opy_)
    bstack1l1ll1l_opy_ = True
    bstack1l1l1lll1_opy_ = 1
    if bstack1ll1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩര") in CONFIG:
      bstack1l1l1lll1_opy_ = CONFIG[bstack1ll1_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪറ")]
    bstack11l1ll_opy_ = int(bstack1l1l1lll1_opy_)*int(len(CONFIG[bstack1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧല")]))
    execution_items = []
    for index, _ in enumerate(CONFIG[bstack1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨള")]):
      for bstack111l11_opy_ in bstack1lllll11l_opy_:
        item = {}
        item[bstack1ll1_opy_ (u"࠭ࡡࡳࡩࠪഴ")] = bstack111l11_opy_
        item[bstack1ll1_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭വ")] = index
        execution_items.append(item)
    bstack111111l1_opy_ = bstack11l1lll_opy_(execution_items, bstack11l1ll_opy_)
    for execution_item in bstack111111l1_opy_:
      bstack1l1l1111_opy_ = []
      for item in execution_item:
        bstack1l1l1111_opy_.append(bstack11lll1ll_opy_(name=str(item[bstack1ll1_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧശ")]),
                                            target=bstack1l11l1ll_opy_,
                                            args=(item[bstack1ll1_opy_ (u"ࠩࡤࡶ࡬࠭ഷ")],)))
      for t in bstack1l1l1111_opy_:
        t.start()
      for t in bstack1l1l1111_opy_:
        t.join()
  elif bstack1l1ll1lll_opy_ == bstack1ll1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪസ"):
    try:
      from behave.__main__ import main as bstack1111lll_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack11l1_opy_(e, bstack1l111ll_opy_)
    bstack1l1l1111l_opy_()
    bstack1l1ll1l_opy_ = True
    bstack1l1l1lll1_opy_ = 1
    if bstack1ll1_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫഹ") in CONFIG:
      bstack1l1l1lll1_opy_ = CONFIG[bstack1ll1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬഺ")]
    bstack11l1ll_opy_ = int(bstack1l1l1lll1_opy_)*int(len(CONFIG[bstack1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴ഻ࠩ")]))
    config = Configuration(args)
    bstack1l1ll11l_opy_ = config.paths
    bstack11l11l11_opy_ = []
    for arg in args:
      if os.path.normpath(arg) not in bstack1l1ll11l_opy_:
        bstack11l11l11_opy_.append(arg)
    import platform as pf
    if pf.system().lower() == bstack1ll1_opy_ (u"ࠧࡸ࡫ࡱࡨࡴࡽࡳࠨ഼"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1l1ll11l_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11lll_opy_)))
                    for bstack11lll_opy_ in bstack1l1ll11l_opy_]
    bstack1lllll11l_opy_ = []
    for spec in bstack1l1ll11l_opy_:
      bstack111l11_opy_ = []
      bstack111l11_opy_ += bstack11l11l11_opy_
      bstack111l11_opy_.append(spec)
      bstack1lllll11l_opy_.append(bstack111l11_opy_)
    execution_items = []
    for index, _ in enumerate(CONFIG[bstack1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫഽ")]):
      for bstack111l11_opy_ in bstack1lllll11l_opy_:
        item = {}
        item[bstack1ll1_opy_ (u"ࠩࡤࡶ࡬࠭ാ")] = bstack1ll1_opy_ (u"ࠪࠤࠬി").join(bstack111l11_opy_)
        item[bstack1ll1_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪീ")] = index
        execution_items.append(item)
    bstack111111l1_opy_ = bstack11l1lll_opy_(execution_items, bstack11l1ll_opy_)
    for execution_item in bstack111111l1_opy_:
      bstack1l1l1111_opy_ = []
      for item in execution_item:
        bstack1l1l1111_opy_.append(bstack11lll1ll_opy_(name=str(item[bstack1ll1_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫു")]),
                                            target=bstack1l1111l_opy_,
                                            args=(item[bstack1ll1_opy_ (u"࠭ࡡࡳࡩࠪൂ")],)))
      for t in bstack1l1l1111_opy_:
        t.start()
      for t in bstack1l1l1111_opy_:
        t.join()
  else:
    bstack1ll1lll_opy_(bstack1111l1l1_opy_)
  bstack1l1l11lll_opy_()
def bstack1l1l11lll_opy_():
  global CONFIG
  try:
    if bstack1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪൃ") in CONFIG:
      host = bstack1ll1_opy_ (u"ࠨࡣࡳ࡭࠲ࡩ࡬ࡰࡷࡧࠫൄ") if bstack1ll1_opy_ (u"ࠩࡤࡴࡵ࠭൅") in CONFIG else bstack1ll1_opy_ (u"ࠪࡥࡵ࡯ࠧെ")
      user = CONFIG[bstack1ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭േ")]
      key = CONFIG[bstack1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨൈ")]
      bstack1l1ll1l11_opy_ = bstack1ll1_opy_ (u"࠭ࡡࡱࡲ࠰ࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ൉") if bstack1ll1_opy_ (u"ࠧࡢࡲࡳࠫൊ") in CONFIG else bstack1ll1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧࠪോ")
      url = bstack1ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡿࢂࡀࡻࡾࡂࡾࢁ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡽࢀ࠳ࡧࡻࡩ࡭ࡦࡶ࠲࡯ࡹ࡯࡯ࠩൌ").format(user, key, host, bstack1l1ll1l11_opy_)
      headers = {
        bstack1ll1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦ്ࠩ"): bstack1ll1_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧൎ"),
      }
      if bstack1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ൏") in CONFIG:
        params = {bstack1ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ൐"):CONFIG[bstack1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ൑")], bstack1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ൒"):CONFIG[bstack1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ൓")]}
      else:
        params = {bstack1ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨൔ"):CONFIG[bstack1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧൕ")]}
      response = requests.get(url, params=params, headers=headers)
      if response.json():
        bstack1ll1l1lll_opy_ = response.json()[0][bstack1ll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡥࡹ࡮ࡲࡤࠨൖ")]
        if bstack1ll1l1lll_opy_:
          bstack11ll11l1_opy_ = bstack1ll1l1lll_opy_[bstack1ll1_opy_ (u"࠭ࡰࡶࡤ࡯࡭ࡨࡥࡵࡳ࡮ࠪൗ")].split(bstack1ll1_opy_ (u"ࠧࡱࡷࡥࡰ࡮ࡩ࠭ࡣࡷ࡬ࡰࡩ࠭൘"))[0] + bstack1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡳ࠰ࠩ൙") + bstack1ll1l1lll_opy_[bstack1ll1_opy_ (u"ࠩ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬ൚")]
          logger.info(bstack1lll11_opy_.format(bstack11ll11l1_opy_))
          bstack1lll111l1_opy_ = CONFIG[bstack1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭൛")]
          if bstack1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭൜") in CONFIG:
            bstack1lll111l1_opy_ += bstack1ll1_opy_ (u"ࠬࠦࠧ൝") + CONFIG[bstack1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ൞")]
          if bstack1lll111l1_opy_!= bstack1ll1l1lll_opy_[bstack1ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬൟ")]:
            logger.debug(bstack1111_opy_.format(bstack1ll1l1lll_opy_[bstack1ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ൠ")], bstack1lll111l1_opy_))
    else:
      logger.warn(bstack11ll1ll_opy_)
  except Exception as e:
    logger.debug(bstack11ll1l1_opy_.format(str(e)))
def bstack1lll111_opy_(url, bstack1l1l111l_opy_=False):
  global CONFIG
  global bstack1l1ll_opy_
  if not bstack1l1ll_opy_:
    hostname = bstack1l11ll11_opy_(url)
    is_private = bstack1ll11l11_opy_(hostname)
    if (bstack1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭ൡ") in CONFIG and not CONFIG[bstack1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧൢ")]) and (is_private or bstack1l1l111l_opy_):
      bstack1l1ll_opy_ = hostname
def bstack1l11ll11_opy_(url):
  return urlparse(url).hostname
def bstack1ll11l11_opy_(hostname):
  for bstack1l1l11ll1_opy_ in bstack1lll111ll_opy_:
    regex = re.compile(bstack1l1l11ll1_opy_)
    if regex.match(hostname):
      return True
  return False