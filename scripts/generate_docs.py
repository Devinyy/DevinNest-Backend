import json
import httpx
import sys

def get_schema_example(schema, components, depth=0):
    if depth > 2: # Avoid infinite recursion
        return "..."
        
    if '$ref' in schema:
        ref_name = schema['$ref'].split('/')[-1]
        ref_schema = components.get(ref_name, {})
        return get_schema_example(ref_schema, components, depth + 1)
    
    if 'type' not in schema and 'properties' in schema:
         schema['type'] = 'object'

    type_ = schema.get('type')
    
    if type_ == 'object':
        example = {}
        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            example[prop_name] = get_schema_example(prop_schema, components, depth + 1)
        return example
    
    if type_ == 'array':
        items_schema = schema.get('items', {})
        return [get_schema_example(items_schema, components, depth + 1)]
    
    if type_ == 'string':
        return schema.get('example', "string")
    if type_ == 'integer':
        return schema.get('example', 0)
    if type_ == 'number':
        return schema.get('example', 0.0)
    if type_ == 'boolean':
        return schema.get('example', True)
        
    return "any"

def indent_text(text, prefix="  "):
    return "\n".join(prefix + line for line in text.splitlines())

def generate_markdown(openapi_url, output_file):
    try:
        response = httpx.get(openapi_url)
        response.raise_for_status()
        schema = response.json()
    except Exception as e:
        print(f"Error fetching OpenAPI schema: {e}")
        return

    components = schema.get('components', {}).get('schemas', {})
    
    md = f"# {schema.get('info', {}).get('title', 'API Documentation')}\n\n"
    md += "本文档描述了 Devin's Nest 后台管理系统所需的后端 API 接口。\n\n"
    
    md += "## 1. 基础说明\n\n"
    md += "- **Base URL**: `/api/v1`\n"
    md += "- **认证方式**: Bearer Token (Header: `Authorization: Bearer <token>`)\n"
    md += "- **数据格式**: JSON\n"
    md += "- **响应结构**:\n\n"
    md += "```typescript\n"
    md += "interface ApiResponse<T> {\n"
    md += "  code: number;      // 200: 成功, 非 200: 失败\n"
    md += "  message: string;   // 提示信息\n"
    md += "  data: T;           // 业务数据\n"
    md += "}\n"
    md += "```\n\n"

    # Group by tags
    tags_map = {}
    paths = schema.get('paths', {})
    
    for path, methods in paths.items():
        for method, details in methods.items():
            tags = details.get('tags', ['Other'])
            for tag in tags:
                if tag not in tags_map:
                    tags_map[tag] = []
                tags_map[tag].append({
                    'path': path,
                    'method': method.upper(),
                    'details': details
                })

    section_idx = 2
    
    # Custom order for tags if needed
    tag_order = [
        "backstage-auth", 
        "backstage-dashboard", 
        "backstage-blogs", 
        "backstage-snippets", 
        "backstage-taxonomy",
        "backstage-common"
    ]
    
    # Add remaining tags
    for tag in tags_map.keys():
        if tag not in tag_order:
            tag_order.append(tag)

    for tag in tag_order:
        if tag not in tags_map:
            continue
            
        endpoints = tags_map[tag]
        
        # Friendly Tag Names
        tag_name_map = {
            "backstage-auth": "认证模块 (Auth)",
            "backstage-dashboard": "仪表盘 (Dashboard)",
            "backstage-blogs": "博客管理 (Blogs)",
            "backstage-snippets": "碎片管理 (Snippets)",
            "backstage-taxonomy": "分类与标签 (Taxonomy)",
            "backstage-common": "通用接口 (Common)",
            "nest-projects": "DevinNest 项目 (Projects)",
            "ai": "AI 服务 (LLM)"
        }
        
        friendly_tag_name = tag_name_map.get(tag, tag.capitalize())
        
        md += f"## {section_idx}. {friendly_tag_name}\n\n"
        
        sub_idx = 1
        for endpoint in endpoints:
            path = endpoint['path']
            method = endpoint['method']
            details = endpoint['details']
            summary = details.get('summary', 'No Summary')
            description = details.get('description', '')
            
            md += f"### {section_idx}.{sub_idx} {summary}\n"
            md += f"- **URL**: `{path}`\n"
            md += f"- **Method**: `{method}`\n"
            if description:
                md += f"- **描述**: {description}\n"
            
            # Request Parameters
            params = details.get('parameters', [])
            query_params = [p for p in params if p['in'] == 'query']
            if query_params:
                md += "- **Query 参数**:\n"
                for param in query_params:
                    name = param['name']
                    desc = param.get('description', '-')
                    required = "(必填)" if param.get('required') else ""
                    md += f"  - `{name}`: {desc} {required}\n"
            
            # Request Body
            if 'requestBody' in details:
                md += "- **请求参数**:\n"
                content = details['requestBody'].get('content', {})
                json_content = content.get('application/json')
                
                if json_content:
                    schema_ref = json_content.get('schema')
                    if schema_ref:
                        example = get_schema_example(schema_ref, components)
                        json_str = json.dumps(example, indent=2, ensure_ascii=False)
                        md += "  ```json\n"
                        md += indent_text(json_str)
                        md += "\n  ```\n"
            
            # Response
            responses = details.get('responses', {})
            success_resp = responses.get('200')
            if success_resp:
                md += "- **响应数据**:\n"
                content = success_resp.get('content', {})
                json_content = content.get('application/json')
                
                if json_content:
                    schema_ref = json_content.get('schema')
                    if schema_ref:
                        example = get_schema_example(schema_ref, components)
                        json_str = json.dumps(example, indent=2, ensure_ascii=False)
                        md += "  ```json\n"
                        md += indent_text(json_str)
                        md += "\n  ```\n"
                    else:
                        md += "  (无返回数据)\n"
                else:
                    md += "  (无返回数据)\n"
            
            md += "\n"
            sub_idx += 1
        
        section_idx += 1

    with open(output_file, 'w') as f:
        f.write(md)
    print(f"Documentation generated at {output_file}")

if __name__ == "__main__":
    generate_markdown("http://127.0.0.1:8000/api/v1/openapi.json", "API_REFERENCE.md")
