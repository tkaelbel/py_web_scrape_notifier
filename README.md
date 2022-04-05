# py_web_scrape_notifier
 A python script that notifies a user via email about specific changes to a website.

 ## Usage
To script uses the `configuration.json` to provide information about the to notify websites.

``` json
{
  "config": [
    {
      "name": "test1",
      "url": "https://www.amazon.de/Apple-MacBook-Pro-Chip-10%E2%80%91Core-CPU-16%E2%80%91Core-GPU/dp/B09JR5JTP3/?_encoding=UTF8&pd_rd_w=78Cqh&pf_rd_p=07a6ea8f-9559-4d3e-86b6-bade19b6ee8e&pf_rd_r=HXVYGW3RVYEDR4AG9FHP&pd_rd_r=1ff8df8c-2834-4239-826d-e158795c3ba0&pd_rd_wg=hfjFi&ref_=pd_gw_ci_mcx_mr_hp_atf_m",
      "time": 1,
      "cssSelector": ".a-price-whole",
      "condition": "== True"
    },
    {
      "name": "test2",
      "url": "https://www.amazon.de/Apple-MacBook-Pro-Chip-10%E2%80%91Core-CPU-16%E2%80%91Core-GPU/dp/B09JR5JTP3/?_encoding=UTF8&pd_rd_w=78Cqh&pf_rd_p=07a6ea8f-9559-4d3e-86b6-bade19b6ee8e&pf_rd_r=HXVYGW3RVYEDR4AG9FHP&pd_rd_r=1ff8df8c-2834-4239-826d-e158795c3ba0&pd_rd_wg=hfjFi&ref_=pd_gw_ci_mcx_mr_hp_atf_m",
      "time": 1,
      "cssSelector": ".a-price-whole",
      "condition": "<= 2500"
    }
  ]
}
```

* name
