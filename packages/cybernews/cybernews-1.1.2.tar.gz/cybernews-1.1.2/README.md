<h1>cybernews</h1>
Python package and API that provides latest Cyber Security updates from various sources under one roof and use Web-Scraping under the hood.

<br>
<h2>Features :-</h2>

```
News Headlines
News Author
Full News
News Article URL
News Image
News Date
```
<br>
Developed by GhoulBond (c) 2023<br><br>

<h2>Setup</h2>


<h3>For Window Users</h3>

```python
pip install cybernews 
```

<h3>For Linux/Mac Users</h3>

```python
pip3 install cybernews
```

<h2>Use</h2>

```python
from cybernews.cybernews import CyberNews

news = CyberNews() # Instance is created
```

| **S.No.** | **Operation**      | **Functions**                 |
|-----------|--------------------|-------------------------------|
| 1         | General News       | news.get_news("general")      |
| 2         | Data Breach News   | news.get_news("dataBreach")   |
| 3         | Cyber Attack News  | news.get_news("cyberAttack")  |
| 4         | Vulnerability News | news.get_news("vulenrability")|
| 5         | Malware News       | news.get_news("malware")      |
| 6         | Security News      | news.get_news("security")     |
| 7         | Cloud News         | news.get_news("cloud")        |
| 8         | Tech News          | news.get_news("tech")         |
| 9         | IOT News           | news.get_news("iot")          |
| 10        | Big Data News      | news.get_news("bigData")      |
| 11        | Business News      | news.get_news("business")     |
| 12        | Mobility News      | news.get_news("mobility")     |
| 13        | Research News      | news.get_news("research")     |
| 14        | Corporate News     | news.get_news("corporate")    |
| 15        | Social Media News  | news.get_news("socialMedia")  |