# GM-Info

一个使用Github Actions自动从官网下载国漫规划备案公示文件并上传到仓库的项目。目前设计为每两周到官网检查一次。

### 项目结构

```
your-repo/
├── .github/
│   └── workflows/
│       └── weekly-scraper.yml   <-- GitHub Actions脚本
├── pdfs/                        <-- 国漫规划备案公示PDF文件
├── scraper.py                   <-- 爬虫脚本
├── requirements.txt             <-- 依赖包列表
└── README.md
```
