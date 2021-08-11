from TM1py import TM1Service

from pyrock import cube_view_create_mdx_statement

tm1 = TM1Service(address="", port=12354, ssl=True, user="admin", password="apple")
print(tm1.server.get_product_version())

cube_name = "c1"
bedrock_filter = "d1:e1+e2&d2:e3"

mdx = cube_view_create_mdx_statement(
    tm1=tm1,
    cube_name=cube_name,
    cube_filter=bedrock_filter)

df = tm1.cells.execute_mdx_dataframe(mdx)

print(df)
