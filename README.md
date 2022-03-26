# Stock-Valuation-Test-Algorithm
This algorithm judges stocks in the S&amp;P 500 based on a multitude of metrics and recommends the top 20 it deems undervalued
It uses test data from IEXFinance sandbox mode api. Obviously not financial advice this is just a fun project for practice.

It judges stocks based on the following metrics.
1) Price to Earnings Ratio
2) Price to Book Ratio
3) Price to Sales Ratio
4) EV/EBITDA ratio
5) EV/GP Ratio
6) Stock price momentum

it places each stock from the snp500 into different percentiles for each of these metrics and picks the top 20 stocks on the best average percentiles
