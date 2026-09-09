from llama_index.core.schema import TextNode, NodeRelationship, RelatedNodeInfo, ImageNode

#创建文本节点,TextNode是文本节点,ImageNode是图片节点,RelatedNodeInfo是相关节点信息,NodeRelationship是节点关系
node1=TextNode(text="deepseek",id="1")
node2=TextNode(text="qwen",id="2")
#node2=ImageNode("node2.png")

#设置node1的下一个节点为node2
node1.relationships[NodeRelationship.NEXT]=RelatedNodeInfo(
    node_id=node2.id_,
    metadata={"desc":"node1的下一个节点是node2"}
)

#设置node2的上一个节点为node1
node2.relationships[NodeRelationship.PREVIOUS]=RelatedNodeInfo(
    node_id=node1.id_,
    metadata={"desc":"node2的上一个节点是node1"}
)

nodes=[node1,node2]
print(nodes)