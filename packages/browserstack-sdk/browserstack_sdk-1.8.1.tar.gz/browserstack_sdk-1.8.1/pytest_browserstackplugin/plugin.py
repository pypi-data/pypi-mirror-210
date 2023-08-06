# coding: UTF-8
import sys
bstack11_opy_ = sys.version_info [0] == 2
bstack1_opy_ = 2048
bstack1l_opy_ = 7
def bstack1l1_opy_ (bstack11ll_opy_):
    global bstack11l_opy_
    stringNr = ord (bstack11ll_opy_ [-1])
    bstack1lll_opy_ = bstack11ll_opy_ [:-1]
    bstack111l_opy_ = stringNr % len (bstack1lll_opy_)
    bstack1111_opy_ = bstack1lll_opy_ [:bstack111l_opy_] + bstack1lll_opy_ [bstack111l_opy_:]
    if bstack11_opy_:
        bstack1ll_opy_ = unicode () .join ([unichr (ord (char) - bstack1_opy_ - (bstack1llll_opy_ + stringNr) % bstack1l_opy_) for bstack1llll_opy_, char in enumerate (bstack1111_opy_)])
    else:
        bstack1ll_opy_ = str () .join ([chr (ord (char) - bstack1_opy_ - (bstack1llll_opy_ + stringNr) % bstack1l_opy_) for bstack1llll_opy_, char in enumerate (bstack1111_opy_)])
    return eval (bstack1ll_opy_)
import pytest
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
def bstack1ll1_opy_(page, bstack11l1_opy_):
  try:
    page.evaluate(bstack1l1_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧࠀ"), bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠩࠁ")+ json.dumps(bstack11l1_opy_) + bstack1l1_opy_ (u"ࠨࡽࡾࠤࠂ"))
  except Exception as e:
    print(bstack1l1_opy_ (u"ࠢࡦࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢࡾࢁࠧࠃ"), e)
def bstack111_opy_(page, message, level):
  try:
    page.evaluate(bstack1l1_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤࠄ"), bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧࠅ") + json.dumps(message) + bstack1l1_opy_ (u"ࠪ࠰ࠧࡲࡥࡷࡧ࡯ࠦ࠿࠭ࠆ") + json.dumps(level) + bstack1l1_opy_ (u"ࠫࢂࢃࠧࠇ"))
  except Exception as e:
    print(bstack1l1_opy_ (u"ࠧ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡣࡱࡲࡴࡺࡡࡵ࡫ࡲࡲࠥࢁࡽࠣࠈ"), e)
def bstackl_opy_(page, status, message = bstack1l1_opy_ (u"ࠨࠢࠉ")):
  try:
    if(status == bstack1l1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢࠊ")):
      page.evaluate(bstack1l1_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤࠋ"), bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡴࡨࡥࡸࡵ࡮ࠣ࠼ࠪࠌ") + json.dumps(bstack1l1_opy_ (u"ࠥࡗࡨ࡫࡮ࡢࡴ࡬ࡳࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡽࡩࡵࡪ࠽ࠤࠧࠍ") + str(message)) + bstack1l1_opy_ (u"ࠫ࠱ࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠨࠎ") + json.dumps(status) + bstack1l1_opy_ (u"ࠧࢃࡽࠣࠏ"))
    else:
      page.evaluate(bstack1l1_opy_ (u"ࠨ࡟ࠡ࠿ࡁࠤࢀࢃࠢࠐ"), bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠨࠑ") + json.dumps(status) + bstack1l1_opy_ (u"ࠣࡿࢀࠦࠒ"))
  except Exception as e:
    print(bstack1l1_opy_ (u"ࠤࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠥࡹࡥࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣࡿࢂࠨࠓ"), e)
@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    plugins = item.config.getoption(bstack1l1_opy_ (u"ࠥࡴࡱࡻࡧࡪࡰࡶࠦࠔ"))
    if(bstack1l1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡳࡰࡺ࡭ࡩ࡯ࠤࠕ") not in plugins):
        return
    report = outcome.get_result()
    summary = []
    driver = getattr(item, bstack1l1_opy_ (u"ࠧࡥࡤࡳ࡫ࡹࡩࡷࠨࠖ"), None)
    page = getattr(item, bstack1l1_opy_ (u"ࠨ࡟ࡱࡣࡪࡩࠧࠗ"), None)
    if(driver is not None):
        bstack1l1l_opy_(item, report, summary)
    if(page is not None):
        bstack1l11_opy_(item, report, summary)
def bstack1l1l_opy_(item, report, summary):
    if report.when in [bstack1l1_opy_ (u"ࠢࡴࡧࡷࡹࡵࠨ࠘"), bstack1l1_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࠥ࠙")]:
            return
    item._driver.execute_script(bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨ࡮ࡢ࡯ࡨࠦ࠿ࠦࠧࠚ") + json.dumps(report.nodeid) + bstack1l1_opy_ (u"ࠪࢁࢂ࠭ࠛ"))
    passed = report.passed or (report.failed and hasattr(report, bstack1l1_opy_ (u"ࠦࡼࡧࡳࡹࡨࡤ࡭ࡱࠨࠜ")))
    bstack1lll1_opy_ = bstack1l1_opy_ (u"ࠧࠨࠝ")
    if not passed:
        try:
            bstack1lll1_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack1l1_opy_ (u"ࠨࡗࡂࡔࡑࡍࡓࡍ࠺ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡩ࡫ࡴࡦࡴࡰ࡭ࡳ࡫ࠠࡧࡣ࡬ࡰࡺࡸࡥࠡࡴࡨࡥࡸࡵ࡮࠻ࠢࡾ࠴ࢂࠨࠞ").format(e)
            )
    try:
        if passed:
            item._driver.execute_script(
                bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠤࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ࠲ࠠ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠢࠥࡷࡹࡧࡴࡶࡵࠥ࠾ࠧࡶࡡࡴࡵࡨࡨࠧࠦࡽࠡ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢃࠧࠟ")
            )
        else:
            if bstack1lll1_opy_:
                item._driver.execute_script(
                    bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡥࡳࡴࡲࡶࠧ࠲ࠠ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡨࡦࡺࡡࠣ࠼ࠣࠫࠠ")
                    + json.dumps(str(bstack1lll1_opy_))
                    + bstack1l1_opy_ (u"ࠤ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡾ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࢀࠦࠡ")
                )
                item._driver.execute_script(
                    bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠢࠥࡪࡦ࡯࡬ࡦࡦࠥ࠰ࠥࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣࡴࡨࡥࡸࡵ࡮ࠣ࠼ࠣࠫࠢ")
                    + json.dumps(str(bstack1lll1_opy_))
                    + bstack1l1_opy_ (u"ࠦࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࢀࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࢂࠨࠣ")
                )
            else:
                item._driver.execute_script(
                    bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠢ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢ࠭ࠢ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠡࠤࡶࡸࡦࡺࡵࡴࠤ࠽ࠦ࡫ࡧࡩ࡭ࡧࡧࠦࠥࢃࠠ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿࠪࠤ")
                )
    except Exception as e:
        summary.append(bstack1l1_opy_ (u"ࠨࡗࡂࡔࡑࡍࡓࡍ࠺ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡺࡶࡤࡢࡶࡨࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷ࠿ࠦࡻ࠱ࡿࠥࠥ").format(e))
def bstack1l11_opy_(item, report, summary):
    if report.when in [bstack1l1_opy_ (u"ࠢࡴࡧࡷࡹࡵࠨࠦ"), bstack1l1_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࠥࠧ")]:
            return
    bstack1ll1_opy_(item._page, report.nodeid)
    passed = report.passed or (report.failed and hasattr(report, bstack1l1_opy_ (u"ࠤࡺࡥࡸࡾࡦࡢ࡫࡯ࠦࠨ")))
    bstack1lll1_opy_ = bstack1l1_opy_ (u"ࠥࠦࠩ")
    if not passed:
        try:
            bstack1lll1_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack1l1_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡧࡩࡹ࡫ࡲ࡮࡫ࡱࡩࠥ࡬ࡡࡪ࡮ࡸࡶࡪࠦࡲࡦࡣࡶࡳࡳࡀࠠࡼ࠲ࢀࠦࠪ").format(e)
            )
    try:
        if passed:
            bstackl_opy_(item._page, bstack1l1_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧࠫ"))
        else:
            if bstack1lll1_opy_:
                bstack111_opy_(item._page, str(bstack1lll1_opy_), bstack1l1_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧࠬ"))
                bstackl_opy_(item._page, bstack1l1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢ࠭"), str(bstack1lll1_opy_))
            else:
                bstackl_opy_(item._page, bstack1l1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ࠮"))
    except Exception as e:
        summary.append(bstack1l1_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡶࡲࡧࡥࡹ࡫ࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳ࠻ࠢࡾ࠴ࢂࠨ࠯").format(e))
try:
    from typing import Generator
    import pytest_playwright.pytest_playwright as p
    @pytest.fixture
    def page(context: BrowserContext, request: pytest.FixtureRequest) -> Generator[Page, None, None]:
        page = context.new_page()
        request.node._page = page
        yield page
except:
    pass
def pytest_addoption(parser):
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack1l1_opy_ (u"ࠥ࠱࠲ࡪࡲࡪࡸࡨࡶࠧ࠰"), action=bstack1l1_opy_ (u"ࠦࡸࡺ࡯ࡳࡧࠥ࠱"), default=bstack1l1_opy_ (u"ࠧࡩࡨࡳࡱࡰࡩࠧ࠲"),
                        help=bstack1l1_opy_ (u"ࠨࡄࡳ࡫ࡹࡩࡷࠦࡴࡰࠢࡵࡹࡳࠦࡴࡦࡵࡷࡷࠧ࠳"))