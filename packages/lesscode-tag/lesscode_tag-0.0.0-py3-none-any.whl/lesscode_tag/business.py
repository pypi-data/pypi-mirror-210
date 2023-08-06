from lesscode_tag.es_util import es_condition_by_terms, es_condition_by_wildcard


def format_param_tag(bool_should_more_list, especial_tag_list, is_need_decrypt=False, aes_key="haohaoxuexi"):
    bool_should_list = []
    if especial_tag_list is not None:
        for tag in especial_tag_list:

            if tag == "省级专精特新":
                bool_should_list.append({"bool": {"must": [
                    {"terms": {"tags.diy_tag": ["省级专精特新企业"]}},
                    {"bool": {"must_not": [{"terms": {"tags.diy_tag": ["国家级专精特新企业"]}}]}}
                ]
                }
                })
            if tag in ["国家级专精特新", "国家级单项冠军", "瞪羚"]:
                es_condition_by_terms(bool_must_list=bool_should_list, column="tags.diy_tag", param_list=[tag + "企业"],
                                      is_need_decrypt=is_need_decrypt, key=aes_key)
            if tag in ["高新技术企业", "央企", "瞪羚企业", "中国企业500强"]:
                es_condition_by_terms(bool_must_list=bool_should_list, column="tags.diy_tag", param_list=[tag],
                                      is_need_decrypt=is_need_decrypt, key=aes_key)
            if tag in ["单项冠军"]:
                es_condition_by_terms(bool_must_list=bool_should_list, column="tags.diy_tag",
                                      param_list=["国家级单项冠军企业"],
                                      is_need_decrypt=is_need_decrypt, key=aes_key)
            if tag in ["专精特新"]:
                es_condition_by_terms(bool_must_list=bool_should_list, column="tags.diy_tag",
                                      param_list=["省级专精特新企业", "国家级专精特新企业"],
                                      is_need_decrypt=is_need_decrypt, key=aes_key)
            # 上市信息
            if tag in ["A股上市"]:
                bool_should_list.append({"bool": {"must": [
                    {"terms": {"tags.market_tag.block": ["主板上市", "科创板上市", "创业板上市", "北交所"]}},
                    {"terms": {"tags.market_tag.status": ["已上市"]}}
                ]
                }
                })
            if tag in ["新三板"]:
                es_condition_by_terms(bool_must_list=bool_should_list, column="tags.market_tag.status",
                                      param_list=["新三板挂牌"],
                                      is_need_decrypt=is_need_decrypt, key=aes_key)
            if tag in ["已上市", "排队上市", "已退市"]:
                es_condition_by_terms(bool_must_list=bool_should_list, column="tags.market_tag.status",
                                      param_list=[tag],
                                      is_need_decrypt=is_need_decrypt, key=aes_key)
            if tag in ["主板上市", "创业板上市", "科创板上市", "新三板-基础层", "新三板-创新层", "新三板-精选层",
                       "北交所"]:
                es_condition_by_terms(bool_must_list=bool_should_list, column="tags.market_tag.block", param_list=[tag],
                                      is_need_decrypt=is_need_decrypt, key=aes_key)
            # 其他  -此类不标准，尽量不要使用
            if tag in ["小巨人", "一条龙"]:
                es_condition_by_wildcard(bool_should_list, "tags.national_tag.tag_name", tag)
            if tag in ["隐形冠军", "成长", "小巨人", "首台套", "雏鹰", "省级单项冠军"]:
                es_condition_by_wildcard(bool_should_list, "tags.province_tag.tag_name", tag)
            if tag in ["雏鹰"]:
                es_condition_by_wildcard(bool_should_list, "tags.city_tag.tag_name", tag)
            if tag in ["雏鹰"]:
                es_condition_by_wildcard(bool_should_list, "tags.district_tag.tag_name", tag)
            if tag in ["独角兽"]:
                es_condition_by_wildcard(bool_should_list, "tags.rank_tag.rank_name", tag)
            if tag in ["科技型中小企业"]:
                es_condition_by_terms(bool_must_list=bool_should_list, column="tags.certification.certification_name",
                                      param_list=[tag],
                                      is_need_decrypt=is_need_decrypt, key=aes_key)
            if tag in ["规上企业"]:
                es_condition_by_terms(bool_must_list=bool_should_list, column="tags.nonpublic_tag", param_list=[tag],
                                      is_need_decrypt=is_need_decrypt, key=aes_key)
    bool_should_more_list.append(bool_should_list)
