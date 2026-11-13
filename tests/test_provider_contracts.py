import unittest
from unittest.mock import Mock, patch

from nselib.capital_market import capital_market_data
from nselib import libutil


class TestBhavCopySme(unittest.TestCase):
    def test_sme_url_uses_eight_digit_date(self):
        response = Mock()
        response.status_code = 200
        response.content = b"SYMBOL,SERIES\n"
        with patch.object(capital_market_data, "nse_urlfetch", return_value=response) as fetch, patch.object(
            capital_market_data.pd, "read_csv", return_value=Mock(columns=[])
        ):
            capital_market_data.bhav_copy_sme("13-11-2026")
        self.assertIn("sme13112026.csv", fetch.call_args.args[0])


class TestEquityList(unittest.TestCase):
    def test_equity_list_includes_isin(self):
        response = Mock()
        response.status_code = 200
        response.content = (
            b"SYMBOL,NAME OF COMPANY,SERIES,DATE OF LISTING,PAID UP VALUE,"
            b"MARKET LOT,ISIN NUMBER,FACE VALUE\n"
        )
        frame = capital_market_data.pd.DataFrame(
            [
                {
                    "SYMBOL": "TCS",
                    "NAME OF COMPANY": "Tata Consultancy Services",
                    "SERIES": "EQ",
                    "DATE OF LISTING": "25-AUG-2004",
                    "PAID UP VALUE": "1.00",
                    "MARKET LOT": "1",
                    "ISIN NUMBER": "INE467B01029",
                    "FACE VALUE": "1.00",
                }
            ]
        )
        with patch.object(libutil, "nse_urlfetch", return_value=response), patch.object(
            capital_market_data, "nse_urlfetch", return_value=response
        ), patch.object(capital_market_data.pd, "read_csv", return_value=frame):
            result = capital_market_data.equity_list()
        self.assertIn("ISIN NUMBER", result.columns)
        self.assertEqual(result.iloc[0]["ISIN NUMBER"], "INE467B01029")


class TestUrlFetchTimeout(unittest.TestCase):
    def test_session_requests_have_timeouts(self):
        session = Mock()
        with patch.object(libutil.requests, "session", return_value=session):
            libutil.nse_urlfetch("https://www.nseindia.com/api/test")
        self.assertEqual(session.get.call_count, 2)
        for call in session.get.call_args_list:
            self.assertEqual(call.kwargs["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
