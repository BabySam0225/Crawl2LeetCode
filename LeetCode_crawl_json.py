# """enhance"""

# import requests
# import json
# import time
# import os
# from datetime import datetime
# from bs4 import BeautifulSoup
# import re

# class LeetCodeSpider:
#     def __init__(self):
#         self.graphql_url = "https://leetcode.cn/graphql/"
#         self.headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Content-Type': 'application/json',
#             'Referer': 'https://leetcode.cn/problemset/',
#             'Origin': 'https://leetcode.cn',
#             'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
#         }
#         self.session = requests.Session()
#         self.session.headers.update(self.headers)
#         self.problems_data = []

#     def graphql_query(self, query, variables=None, max_retries=3):
#         """执行GraphQL查询"""
#         payload = {
#             "query": query,
#             "variables": variables or {}
#         }
        
#         for attempt in range(max_retries):
#             try:
#                 response = self.session.post(
#                     self.graphql_url,
#                     json=payload,
#                     timeout=15
#                 )
                
#                 if response.status_code == 200:
#                     return True, response.json()
#                 else:
#                     print(f"GraphQL请求失败，状态码: {response.status_code}，第{attempt+1}次重试")
#                     if attempt < max_retries - 1:
#                         time.sleep(2)
#                         continue
#                     return False, None
                    
#             except Exception as e:
#                 print(f"GraphQL请求异常: {e}，第{attempt+1}次重试")
#                 if attempt < max_retries - 1:
#                     time.sleep(2)
#                     continue
#                 return False, None
        
#         return False, None

#     def get_problems_list(self, limit=10):
#         """获取题目列表"""
#         print(f"获取LeetCode前{limit}道题目列表...")
        
#         query = """
#         query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
#           problemsetQuestionList(
#             categorySlug: $categorySlug
#             limit: $limit
#             skip: $skip
#             filters: $filters
#           ) {
#             total
#             questions {
#               acRate
#               difficulty
#               frontendQuestionId
#               isFavor
#               paidOnly
#               status
#               title
#               titleCn
#               titleSlug
#               topicTags {
#                 name
#                 nameTranslated
#                 slug
#               }
#             }
#           }
#         }
#         """
        
#         variables = {
#             "categorySlug": "",
#             "skip": 0,
#             "limit": limit,
#             "filters": {}
#         }
        
#         success, data = self.graphql_query(query, variables)
#         if success and data:
#             questions = data.get('data', {}).get('problemsetQuestionList', {}).get('questions', [])
#             print(f"成功获取 {len(questions)} 道题目")
#             return questions
#         else:
#             print("获取题目列表失败")
#             return []

#     def parse_translated_content(self, translated_content):
#         """解析translatedContent，拆分成不同部分"""
#         if not translated_content:
#             return {
#                 'description': '',
#                 'examples': [],
#                 'constraints': '',
#                 'follow_up': ''
#             }
        
#         soup = BeautifulSoup(translated_content, 'html.parser')
        
#         # 提取描述部分（示例之前的所有内容）
#         description_parts = []
#         examples = []
#         constraints = ""
#         follow_up = ""
        
#         current_section = 'description'
        
#         for element in soup.children:
#             if element.name is None:  # 跳过空文本节点
#                 continue
                
#             # 检查是否是示例标题
#             if element.name == 'p' and element.find('strong', class_='example'):
#                 current_section = 'example'
#                 example_title = element.get_text().strip()
#                 example_content = []
#                 examples.append({
#                     'title': example_title,
#                     'content': example_content
#                 })
#                 continue
            
#             # 检查是否是约束条件标题
#             if element.name == 'p' and element.find('strong') and '提示' in element.get_text():
#                 current_section = 'constraints'
#                 constraints_content = []
#                 continue
                
#             # 检查是否是进阶标题
#             if element.name == 'p' and element.find('strong') and '进阶' in element.get_text():
#                 current_section = 'follow_up'
#                 follow_up_content = []
#                 continue
            
#             # 根据当前部分处理内容
#             if current_section == 'description':
#                 description_parts.append(element.get_text().strip())
#             elif current_section == 'example' and examples:
#                 # 处理示例内容
#                 if element.name == 'pre':
#                     examples[-1]['content'].append(f"```\n{element.get_text().strip()}\n```")
#                 else:
#                     text = element.get_text().strip()
#                     if text:
#                         examples[-1]['content'].append(text)
#             elif current_section == 'constraints':
#                 if element.name == 'ul':
#                     constraints = element.get_text().strip()
#                 elif element.name == 'p':
#                     text = element.get_text().strip()
#                     if text and not text.startswith('提示'):
#                         constraints_content.append(text)
#             elif current_section == 'follow_up':
#                 text = element.get_text().strip()
#                 if text and not text.startswith('进阶'):
#                     follow_up_content.append(text)
        
#         # 处理约束条件内容
#         if current_section == 'constraints' and 'constraints_content' in locals():
#             constraints = '\n'.join(constraints_content)
        
#         # 处理进阶内容
#         if current_section == 'follow_up' and 'follow_up_content' in locals():
#             follow_up = '\n'.join(follow_up_content)
        
#         # 清理示例内容
#         cleaned_examples = []
#         for example in examples:
#             content = '\n'.join(example['content'])
#             # 提取输入输出
#             input_match = re.search(r'输入：\s*(.*?)(?=输出：|\n|$)', content, re.DOTALL)
#             output_match = re.search(r'输出：\s*(.*?)(?=解释：|\n|$)', content, re.DOTALL)
#             explanation_match = re.search(r'解释：\s*(.*?)(?=\n|$)', content, re.DOTALL)
            
#             cleaned_examples.append({
#                 'title': example['title'],
#                 'input': input_match.group(1).strip() if input_match else '',
#                 'output': output_match.group(1).strip() if output_match else '',
#                 'explanation': explanation_match.group(1).strip() if explanation_match else '',
#                 'raw_content': content
#             })
        
#         return {
#             'description': '\n'.join(description_parts),
#             'examples': cleaned_examples,
#             'constraints': constraints,
#             'follow_up': follow_up
#         }

#     def get_problem_detail(self, title_slug):
#         """获取题目详细信息"""
#         print(f"获取题目详情: {title_slug}")
        
#         query = """
#         query questionData($titleSlug: String!) {
#           question(titleSlug: $titleSlug) {
#             questionId
#             questionFrontendId
#             title
#             titleCn: translatedTitle
#             content
#             translatedContent
#             difficulty
#             categoryTitle
#             topicTags {
#               name
#               nameTranslated: translatedName
#               slug
#             }
#             codeSnippets {
#               lang
#               langSlug
#               code
#             }
#             hints
#             exampleTestcases
#             sampleTestCase
#             jsonExampleTestcases
#             metaData
#             stats
#             similarQuestions
#             companyTagStats
#           }
#         }
#         """
        
#         variables = {"titleSlug": title_slug}
#         success, data = self.graphql_query(query, variables)
        
#         if success and data:
#             question_data = data.get('data', {}).get('question', {})
            
#             # 如果translatedContent为空，尝试从content生成基本翻译
#             if not question_data.get('translatedContent') and question_data.get('content'):
#                 print(f"题目 {title_slug} 的translatedContent为空，使用英文内容")
#                 question_data['translatedContent'] = self.translate_content_basic(question_data['content'])
            
#             # 如果jsonExampleTestcases为空但exampleTestcases存在，尝试转换
#             if not question_data.get('jsonExampleTestcases') and question_data.get('exampleTestcases'):
#                 question_data['jsonExampleTestcases'] = self.convert_to_json_examples(question_data['exampleTestcases'])
            
#             # 解析translatedContent
#             if question_data.get('translatedContent'):
#                 parsed_content = self.parse_translated_content(question_data['translatedContent'])
#                 question_data.update(parsed_content)
            
#             return question_data
#         else:
#             print(f"获取题目 {title_slug} 详情失败")
#             return {}

#     def translate_content_basic(self, content):
#         """基础的内容翻译（关键词替换）"""
#         if not content:
#             return ""
        
#         translation_map = {
#             'Example 1:': '示例 1:',
#             'Example 2:': '示例 2:',
#             'Example 3:': '示例 3:',
#             'Input:': '输入:',
#             'Output:': '输出:',
#             'Explanation:': '解释:',
#             'Constraints:': '约束条件:',
#             'Follow-up:': '进阶:',
#             'Note:': '注意:',
#             '提示：': '提示:',
#             '提示:': '提示:',
#         }
        
#         translated = content
#         for eng, cn in translation_map.items():
#             translated = translated.replace(eng, cn)
        
#         return translated

#     def convert_to_json_examples(self, examples):
#         """将示例转换为JSON格式"""
#         try:
#             # 如果已经是JSON格式，直接返回
#             if examples.strip().startswith('['):
#                 return examples
            
#             # 否则尝试转换为JSON数组格式
#             lines = examples.strip().split('\n')
#             json_examples = []
#             current_example = ""
            
#             for line in lines:
#                 line = line.strip()
#                 if line:
#                     if current_example:
#                         current_example += "\\n" + line
#                     else:
#                         current_example = line
            
#             if current_example:
#                 json_examples.append(current_example)
            
#             return json.dumps(json_examples, ensure_ascii=False)
            
#         except Exception as e:
#             print(f"转换示例为JSON时出错: {e}")
#             return examples

#     def parse_stats(self, stats_str):
#         """解析统计信息"""
#         try:
#             return json.loads(stats_str)
#         except:
#             return {}

#     def crawl_problems(self, problem_count=10, output_file=None):
#         """爬取题目信息"""
#         print(f"开始爬取 LeetCode 前 {problem_count} 道题目...")
#         print("=" * 60)
        
#         # 获取题目列表
#         problems = self.get_problems_list(problem_count)
        
#         if not problems:
#             print("未获取到题目列表")
#             return None
        
#         # 获取每个题目的详细信息
#         for i, problem in enumerate(problems, 1):
#             print(f"\n[{i}/{len(problems)}] 处理题目: {problem.get('titleCn', problem.get('title'))}")
            
#             title_slug = problem.get('titleSlug')
#             if not title_slug:
#                 print("跳过: 无titleSlug")
#                 continue
                
#             detail = self.get_problem_detail(title_slug)
            
#             # 合并基本信息与详细信息
#             problem_info = {
#                 # # 题目基本信息
#                 # 'questionFrontendId': problem.get('frontendQuestionId'),
#                 # 'title': problem.get('title'),
#                 # 'titleCn': problem.get('titleCn'),
#                 # 'titleSlug': title_slug,
#                 # 'difficulty': problem.get('difficulty'),
#                 # 'acRate': round(problem.get('acRate', 0), 2),
#                 # 'paidOnly': problem.get('paidOnly', False),
                
#                 # 题目详细信息
#                 'question': {
#                     # 'questionId': detail.get('questionId'),
#                     # 'questionFrontendId': detail.get('questionFrontendId'),
#                     # 'title': detail.get('title'),
#                     'translatedTitle': detail.get('titleCn'),
#                     # 'content': detail.get('content'),
#                     # 'translatedContent': detail.get('translatedContent'),  # 保留原始HTML内容
#                     'description': detail.get('description', ''),  # 纯文本描述
#                     'examples': detail.get('examples', []),  # 结构化的示例
#                     'constraints': detail.get('constraints', ''),  # 约束条件
#                     'followUp': detail.get('follow_up', ''),  # 进阶内容
#                     'difficulty': detail.get('difficulty'),
#                     # 'categoryTitle': detail.get('categoryTitle'),
#                     'topicTags': detail.get('topicTags', []),
#                     # 'codeSnippets': detail.get('codeSnippets', []),
#                     'hints': detail.get('hints', []),
#                     'exampleTestcases': detail.get('exampleTestcases'),
#                     'sampleTestCase': detail.get('sampleTestCase'),
#                     'jsonExampleTestcases': detail.get('jsonExampleTestcases'),
#                     # 'metaData': detail.get('metaData'),
#                     # 'similarQuestions': detail.get('similarQuestions', []),
#                     # 'companyTagStats': detail.get('companyTagStats'),
#                 },
                
#                 # 统计信息
#                 # 'stats': self.parse_stats(detail.get('stats', '{}')),
                
#                 # URL
#                 'url': f"https://leetcode.cn/problems/{title_slug}/"
#             }
            
#             self.problems_data.append(problem_info)
#             # print(f"✓ 完成: {problem_info['titleCn']}")
            
#             # 添加延迟
#             if i < len(problems):
#                 delay = 2
#                 print(f"等待 {delay} 秒...")
#                 time.sleep(delay)
        
#         print(f"\n爬取完成！共获取 {len(self.problems_data)} 道题目信息")
        
#         # 保存为JSON文件
#         if self.problems_data:
#             return self.save_to_json(output_file)
#         else:
#             print("未获取到任何题目数据")
#             return None

#     def save_to_json(self, filename=None):
#         """保存数据到JSON文件"""
#         if not filename:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f'leetcode_parsed_{timestamp}.json'
        
#         try:
#             output_data = {
#                 'metadata': {
#                     'source': 'LeetCode GraphQL API',
#                     'crawl_time': datetime.now().isoformat(),
#                     'total_problems': len(self.problems_data),
#                     'version': '2.0'
#                 },
#                 'problems': self.problems_data
#             }
            
#             with open(filename, 'w', encoding='utf-8') as f:
#                 json.dump(output_data, f, ensure_ascii=False, indent=2)
            
#             file_size = os.path.getsize(filename)
#             file_path = os.path.abspath(filename)
            
#             print(f"数据已保存到: {file_path}")
#             print(f"文件大小: {file_size} 字节")
            
#             # 显示详细统计信息
#             self.show_detailed_statistics()
            
#             return file_path
            
#         except Exception as e:
#             print(f"保存JSON文件时出错: {e}")
#             return None

#     def show_detailed_statistics(self):
#         """显示详细统计信息"""
#         print("\n爬取统计:")
#         print("=" * 50)
        
#         total = len(self.problems_data)
        
#         # 统计各字段的完整性
#         fields_to_check = [
#             ('translatedTitle', '中文标题'),
#             ('description', '描述'),
#             ('examples', '示例'),
#             ('constraints', '约束条件'),
#             ('followUp', '进阶'),
#             ('hints', '提示'),
#             ('codeSnippets', '代码片段')
#         ]
        
#         print("字段完整性统计:")
#         for field, description in fields_to_check:
#             count = 0
#             for problem in self.problems_data:
#                 question_data = problem.get('question', {})
#                 field_data = question_data.get(field)
#                 if field_data:
#                     if isinstance(field_data, list):
#                         if len(field_data) > 0:
#                             count += 1
#                     elif isinstance(field_data, str):
#                         if field_data.strip():
#                             count += 1
#                     else:
#                         count += 1
            
#             percentage = (count / total) * 100
#             print(f"  {description}: {count}/{total} ({percentage:.1f}%)")
        
#         # 难度分布
#         difficulties = {}
#         for problem in self.problems_data:
#             diff = problem.get('difficulty', 'Unknown')
#             difficulties[diff] = difficulties.get(diff, 0) + 1
        
#         print(f"\n难度分布:")
#         for diff, count in difficulties.items():
#             print(f"  {diff}: {count} 题")
        
#         # 显示第一题的详细解析结果
#         if self.problems_data:
#             print("\n第一题解析结果示例:")
#             print("=" * 50)
#             first_problem = self.problems_data[0]
#             question = first_problem.get('question', {})
            
#             print(f"标题: {question.get('translatedTitle', first_problem.get('titleCn'))}")
#             print(f"难度: {first_problem.get('difficulty')}")
#             print(f"\n描述:")
#             print(question.get('description', '')[:200] + "..." if question.get('description') else "无")
            
#             print(f"\n示例:")
#             examples = question.get('examples', [])
#             for i, example in enumerate(examples, 1):
#                 print(f"  示例 {i}:")
#                 print(f"    输入: {example.get('input', '')}")
#                 print(f"    输出: {example.get('output', '')}")
#                 print(f"    解释: {example.get('explanation', '')}")
            
#             print(f"\n约束条件:")
#             print(question.get('constraints', '无'))
            
#             print(f"\n进阶:")
#             print(question.get('followUp', '无'))

# def main():
#     """主函数"""
#     spider = LeetCodeSpider()
    
#     try:
#         output_file = spider.crawl_problems(problem_count=10)
        
#         if output_file:
#             print(f"\n🎉 爬取完成！数据已保存到: {output_file}")
#         else:
#             print("\n❌ 爬取失败")
            
#     except KeyboardInterrupt:
#         print("\n\n⚠️ 用户中断爬取")
#     except Exception as e:
#         print(f"\n❌ 爬取过程中发生错误: {e}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     main()


import random
import requests
import json
import time
import os
from datetime import datetime
from bs4 import BeautifulSoup
import re


class LeetCodeSpider:
    def __init__(self):
        self.graphql_url = "https://leetcode.cn/graphql/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://leetcode.cn/problemset/',
            'Origin': 'https://leetcode.cn',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.problems_data = []

    def graphql_query(self, query, variables=None, max_retries=3):
        """执行GraphQL查询"""
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    self.graphql_url,
                    json=payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    return True, response.json()
                else:
                    print(f"GraphQL请求失败，状态码: {response.status_code}，第{attempt+1}次重试")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return False, None
                    
            except Exception as e:
                print(f"GraphQL请求异常: {e}，第{attempt+1}次重试")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return False, None
        
        return False, None

    def get_problems_list(self, limit=10):
        """获取题目列表"""
        print(f"获取LeetCode前{limit}道题目列表...")
        
        query = """
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
          problemsetQuestionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
          ) {
            total
            questions {
              acRate
              difficulty
              frontendQuestionId
              isFavor
              paidOnly
              status
              title
              titleCn
              titleSlug
              topicTags {
                name
                nameTranslated
                slug
              }
            }
          }
        }
        """
        
        variables = {
            "categorySlug": "",
            "skip": 0,
            "limit": limit,
            "filters": {}
        }
        
        success, data = self.graphql_query(query, variables)
        if success and data:
            questions = data.get('data', {}).get('problemsetQuestionList', {}).get('questions', [])
            print(f"成功获取 {len(questions)} 道题目")
            return questions
        else:
            print("获取题目列表失败")
            return []

    def parse_translated_content(self, translated_content):
        """解析translatedContent，拆分成不同部分"""
        if not translated_content:
            return {
                'description': '',
                'examples': [],
                'constraints': '',
                'follow_up': ''
            }
        
        soup = BeautifulSoup(translated_content, 'html.parser')
        
        # 提取描述部分（示例之前的所有内容）
        description_parts = []
        examples = []
        constraints = ""
        follow_up = ""
        
        # 首先提取所有文本内容，用于分析结构
        all_text = soup.get_text()
        
        # 查找示例部分 - 使用多种方法
        example_patterns = [
            r'示例\s*\d+[：:]?(.*?)(?=示例\s*\d+|约束|提示|进阶|$)',
            r'示例\s*\d+[：:]?(.*?)(?=示例|约束|提示|进阶|$)',
            r'示例\s*\d+[：:]?(.*)'
        ]
        
        # 方法1: 使用正则表达式查找示例
        for pattern in example_patterns:
            example_matches = re.findall(pattern, all_text, re.DOTALL)
            if example_matches:
                for i, match in enumerate(example_matches):
                    if match.strip():
                        # 尝试从示例文本中提取输入、输出和解释
                        example_text = match.strip()
                        input_match = re.search(r'输入[：:]\s*(.*?)(?=输出|解释|$)', example_text, re.DOTALL)
                        output_match = re.search(r'输出[：:]\s*(.*?)(?=解释|输入|$)', example_text, re.DOTALL)
                        explanation_match = re.search(r'解释[：:]\s*(.*?)(?=输入|输出|$)', example_text, re.DOTALL)
                        
                        examples.append({
                            'title': f"示例 {i+1}",
                            'input': input_match.group(1).strip() if input_match else '',
                            'output': output_match.group(1).strip() if output_match else '',
                            'explanation': explanation_match.group(1).strip() if explanation_match else '',
                            'raw_content': example_text
                        })
                break
        
        # 方法2: 如果正则没找到，尝试使用BeautifulSoup查找示例
        if not examples:
            # 查找包含"示例"的元素
            example_elements = soup.find_all(string=re.compile(r'示例\s*\d+'))
            for example_element in example_elements:
                example_title = example_element.strip()
                # 获取示例内容 - 可能是下一个元素或父元素的后续元素
                example_content = ""
                
                # 尝试获取下一个兄弟元素
                next_element = example_element.next_element
                while next_element and next_element.name != 'p' and not re.search(r'示例\s*\d+|约束|提示|进阶', str(next_element)):
                    if next_element.name == 'pre':
                        example_content = next_element.get_text().strip()
                        break
                    next_element = next_element.next_element
                
                if example_content:
                    examples.append({
                        'title': example_title,
                        'input': '',
                        'output': '',
                        'explanation': '',
                        'raw_content': example_content
                    })
        
        # 方法3: 查找所有的pre标签作为示例
        if not examples:
            pre_elements = soup.find_all('pre')
            for i, pre in enumerate(pre_elements):
                pre_text = pre.get_text().strip()
                if pre_text and len(pre_text) > 5:  # 确保不是空内容
                    examples.append({
                        'title': f"示例 {i+1}",
                        'input': pre_text,
                        'output': '',
                        'explanation': '',
                        'raw_content': pre_text
                    })
        
        # 提取约束条件
        constraints_match = re.search(r'提示[：:]\s*(.*?)(?=进阶|$)', all_text, re.DOTALL)
        if constraints_match:
            constraints = constraints_match.group(1).strip()
        else:
            # 尝试查找ul列表作为约束条件
            ul_elements = soup.find_all('ul')
            for ul in ul_elements:
                prev_text = ul.find_previous().get_text() if ul.find_previous() else ""
                if '提示' in prev_text or '约束' in prev_text:
                    constraints = ul.get_text().strip()
                    break
        
        # 提取进阶内容
        follow_up_match = re.search(r'进阶[：:]\s*(.*?)(?=示例|约束|提示|$)', all_text, re.DOTALL)
        if follow_up_match:
            follow_up = follow_up_match.group(1).strip()
        
        # 提取描述部分 - 从开始到第一个示例之前
        if examples:
            first_example_pos = all_text.find(examples[0]['title'])
            if first_example_pos != -1:
                description = all_text[:first_example_pos].strip()
            else:
                description = all_text
        else:
            description = all_text
        
        # 清理描述 - 移除约束和进阶部分
        if constraints:
            constraints_pos = description.find('提示')
            if constraints_pos != -1:
                description = description[:constraints_pos].strip()
        
        if follow_up:
            follow_up_pos = description.find('进阶')
            if follow_up_pos != -1:
                description = description[:follow_up_pos].strip()
        
        return {
            'description': description,
            'examples': examples,
            'constraints': constraints,
            'follow_up': follow_up
        }

    def get_problem_detail(self, title_slug):
        """获取题目详细信息"""
        print(f"获取题目详情: {title_slug}")
        
        query = """
        query questionData($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
            questionFrontendId
            title
            titleCn: translatedTitle
            content
            translatedContent
            difficulty
            categoryTitle
            topicTags {
              name
              nameTranslated: translatedName
              slug
            }
            codeSnippets {
              lang
              langSlug
              code
            }
            hints
            exampleTestcases
            sampleTestCase
            jsonExampleTestcases
            metaData
            stats
            similarQuestions
            companyTagStats
          }
        }
        """
        
        variables = {"titleSlug": title_slug}
        success, data = self.graphql_query(query, variables)
        
        if success and data:
            question_data = data.get('data', {}).get('question', {})
            
            # 如果translatedContent为空，尝试从content生成基本翻译
            if not question_data.get('translatedContent') and question_data.get('content'):
                print(f"题目 {title_slug} 的translatedContent为空，使用英文内容")
                question_data['translatedContent'] = self.translate_content_basic(question_data['content'])
            
            # 如果jsonExampleTestcases为空但exampleTestcases存在，尝试转换
            if not question_data.get('jsonExampleTestcases') and question_data.get('exampleTestcases'):
                question_data['jsonExampleTestcases'] = self.convert_to_json_examples(question_data['exampleTestcases'])
            
            # 解析translatedContent
            if question_data.get('translatedContent'):
                parsed_content = self.parse_translated_content(question_data['translatedContent'])
                question_data.update(parsed_content)
            
            return question_data
        else:
            print(f"获取题目 {title_slug} 详情失败")
            return {}

    def translate_content_basic(self, content):
        """基础的内容翻译（关键词替换）"""
        if not content:
            return ""
        
        translation_map = {
            'Example 1:': '示例 1:',
            'Example 2:': '示例 2:',
            'Example 3:': '示例 3:',
            'Input:': '输入:',
            'Output:': '输出:',
            'Explanation:': '解释:',
            'Constraints:': '约束条件:',
            'Follow-up:': '进阶:',
            'Note:': '注意:',
            '提示：': '提示:',
            '提示:': '提示:',
        }
        
        translated = content
        for eng, cn in translation_map.items():
            translated = translated.replace(eng, cn)
        
        return translated

    def convert_to_json_examples(self, examples):
        """将示例转换为JSON格式"""
        try:
            # 如果已经是JSON格式，直接返回
            if examples.strip().startswith('['):
                return examples
            
            # 否则尝试转换为JSON数组格式
            lines = examples.strip().split('\n')
            json_examples = []
            current_example = ""
            
            for line in lines:
                line = line.strip()
                if line:
                    if current_example:
                        current_example += "\\n" + line
                    else:
                        current_example = line
            
            if current_example:
                json_examples.append(current_example)
            
            return json.dumps(json_examples, ensure_ascii=False)
            
        except Exception as e:
            print(f"转换示例为JSON时出错: {e}")
            return examples

    def parse_stats(self, stats_str):
        """解析统计信息"""
        try:
            return json.loads(stats_str)
        except:
            return {}

    def crawl_problems(self, problem_count=10, output_file=None):
        """爬取题目信息"""
        print(f"开始爬取 LeetCode 前 {problem_count} 道题目...")
        print("=" * 60)
        
        # 获取题目列表
        problems = self.get_problems_list(problem_count)
        
        if not problems:
            print("未获取到题目列表")
            return None
        
        # 获取每个题目的详细信息
        for i, problem in enumerate(problems, 1):
            print(f"\n[{i}/{len(problems)}] 处理题目: {problem.get('titleCn', problem.get('title'))}")
            
            title_slug = problem.get('titleSlug')
            if not title_slug:
                print("跳过: 无titleSlug")
                continue
                
            detail = self.get_problem_detail(title_slug)
            
            # 合并基本信息与详细信息
            problem_info = {
                # # 题目基本信息
                # 'questionFrontendId': problem.get('frontendQuestionId'),
                # 'title': problem.get('title'),
                # 'titleCn': problem.get('titleCn'),
                # 'titleSlug': title_slug,
                # 'difficulty': problem.get('difficulty'),
                # 'acRate': round(problem.get('acRate', 0), 2),
                # 'paidOnly': problem.get('paidOnly', False),
                
                # 题目详细信息
                'question': {
                    # 'questionId': detail.get('questionId'),
                    # 'questionFrontendId': detail.get('questionFrontendId'),
                    # 'title': detail.get('title'),
                    'translatedTitle': detail.get('titleCn'),
                    # 'content': detail.get('content'),
                    'translatedContent': detail.get('translatedContent'),  # 保留原始HTML内容
                    'description': detail.get('description', ''),  # 纯文本描述
                    'examples': detail.get('examples', []),  # 结构化的示例
                    'constraints': detail.get('constraints', ''),  # 约束条件
                    'followUp': detail.get('follow_up', ''),  # 进阶内容
                    'difficulty': detail.get('difficulty'),
                    # 'categoryTitle': detail.get('categoryTitle'),
                    'topicTags': detail.get('topicTags', []),
                    # 'codeSnippets': detail.get('codeSnippets', []),
                    'hints': detail.get('hints', []),
                    'exampleTestcases': detail.get('exampleTestcases'),
                    'sampleTestCase': detail.get('sampleTestCase'),
                    'jsonExampleTestcases': detail.get('jsonExampleTestcases'),
                    # 'metaData': detail.get('metaData'),
                    # 'similarQuestions': detail.get('similarQuestions', []),
                    # 'companyTagStats': detail.get('companyTagStats'),
                },
                
                # 统计信息
                # 'stats': self.parse_stats(detail.get('stats', '{}')),
                
                # URL
                # 'url': f"https://leetcode.cn/problems/{title_slug}/"
            }
            
            self.problems_data.append(problem_info)
            
            # 显示示例提取情况
            # examples_count = len(detail.get('examples', []))
            # if examples_count > 0:
                # print(f"✓ 完成: {problem_info['titleCn']} (提取到 {examples_count} 个示例)")
            # else:
                # print(f"⚠ 完成: {problem_info['titleCn']} (未提取到示例)")
            
            # 添加延迟
            if i < len(problems):
                delay = 5
                print(f"等待 {delay} 秒...")
                time.sleep(delay)
        
        print(f"\n爬取完成！共获取 {len(self.problems_data)} 道题目信息")
        
        # 保存为JSON文件
        if self.problems_data:
            return self.save_to_json(output_file)
        else:
            print("未获取到任何题目数据")
            return None

    def save_to_json(self, filename=None):
        """保存数据到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'leetcode_improved_{timestamp}.json'
        
        try:
            output_data = {
                'metadata': {
                    'source': 'LeetCode GraphQL API',
                    'crawl_time': datetime.now().isoformat(),
                    'total_problems': len(self.problems_data),
                    'version': '3.0'
                },
                'problems': self.problems_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            file_size = os.path.getsize(filename)
            file_path = os.path.abspath(filename)
            
            print(f"数据已保存到: {file_path}")
            print(f"文件大小: {file_size} 字节")
            
            # 显示详细统计信息
            self.show_detailed_statistics()
            
            return file_path
            
        except Exception as e:
            print(f"保存JSON文件时出错: {e}")
            return None

    def show_detailed_statistics(self):
        """显示详细统计信息"""
        print("\n爬取统计:")
        print("=" * 50)
        
        total = len(self.problems_data)
        
        # 统计各字段的完整性
        fields_to_check = [
            ('translatedTitle', '中文标题'),
            ('description', '描述'),
            ('examples', '示例'),
            ('constraints', '约束条件'),
            ('followUp', '进阶'),
            ('hints', '提示'),
            ('codeSnippets', '代码片段')
        ]
        
        print("字段完整性统计:")
        for field, description in fields_to_check:
            count = 0
            for problem in self.problems_data:
                question_data = problem.get('question', {})
                field_data = question_data.get(field)
                if field_data:
                    if isinstance(field_data, list):
                        if len(field_data) > 0:
                            count += 1
                    elif isinstance(field_data, str):
                        if field_data.strip():
                            count += 1
                    else:
                        count += 1
            
            percentage = (count / total) * 100
            print(f"  {description}: {count}/{total} ({percentage:.1f}%)")
        
        # 示例统计
        examples_stats = [0, 0, 0, 0]  # 0个, 1个, 2个, 3+个示例
        for problem in self.problems_data:
            examples_count = len(problem.get('question', {}).get('examples', []))
            if examples_count >= 3:
                examples_stats[3] += 1
            elif examples_count == 2:
                examples_stats[2] += 1
            elif examples_count == 1:
                examples_stats[1] += 1
            else:
                examples_stats[0] += 1
        
        print(f"\n示例数量分布:")
        print(f"  无示例: {examples_stats[0]} 题")
        print(f"  1个示例: {examples_stats[1]} 题")
        print(f"  2个示例: {examples_stats[2]} 题")
        print(f"  3+个示例: {examples_stats[3]} 题")
        
        # 难度分布
        difficulties = {}
        for problem in self.problems_data:
            diff = problem.get('difficulty', 'Unknown')
            difficulties[diff] = difficulties.get(diff, 0) + 1
        
        print(f"\n难度分布:")
        for diff, count in difficulties.items():
            print(f"  {diff}: {count} 题")
        
        # 显示第一题的详细解析结果
        if self.problems_data:
            print("\n第一题解析结果示例:")
            print("=" * 50)
            first_problem = self.problems_data[0]
            question = first_problem.get('question', {})
            
            print(f"标题: {question.get('translatedTitle', first_problem.get('titleCn'))}")
            print(f"难度: {first_problem.get('difficulty')}")
            print(f"\n描述:")
            desc = question.get('description', '')
            print(desc[:200] + "..." if len(desc) > 200 else desc or "无")
            
            print(f"\n示例:")
            examples = question.get('examples', [])
            if examples:
                for i, example in enumerate(examples, 1):
                    print(f"  示例 {i}:")
                    if example.get('input'):
                        print(f"    输入: {example.get('input', '')}")
                    if example.get('output'):
                        print(f"    输出: {example.get('output', '')}")
                    if example.get('explanation'):
                        print(f"    解释: {example.get('explanation', '')}")
                    if example.get('raw_content') and not (example.get('input') or example.get('output')):
                        print(f"    内容: {example.get('raw_content', '')}")
            else:
                print("  无示例")
            
            print(f"\n约束条件:")
            print(question.get('constraints', '无'))
            
            print(f"\n进阶:")
            print(question.get('followUp', '无'))

def main():
    """主函数"""
    spider = LeetCodeSpider()
    
    try:
        output_file = spider.crawl_problems(problem_count=50)
        
        if output_file:
            print(f"\n🎉 爬取完成！数据已保存到: {output_file}")
        else:
            print("\n❌ 爬取失败")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断爬取")
    except Exception as e:
        print(f"\n❌ 爬取过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
