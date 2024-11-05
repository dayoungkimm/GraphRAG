#%%
import pandas as pd
import networkx as nx
from datetime import datetime

# %%
# 데이터 로드
log_data_path = './Android_2k.log_structured.csv'
log_data = pd.read_csv(log_data_path)
log_data

#%%[markdown]
## 지식그래프 구축

# 지식 그래프 초기화
G = nx.MultiDiGraph()

#%%
# 시간 형식 변환 함수
def parse_datetime(date_str, time_str):
    return datetime.strptime(f"{date_str} {time_str}", "%m-%d %H:%M:%S.%f")

# 로그 데이터를 순회하여 노드 간의 엣지를 추가
for i in range(len(log_data) - 1):
    current_component = log_data.iloc[i]['Component']
    current_event = log_data.iloc[i]['EventId']
    current_content = log_data.iloc[i]['Content']
    current_time = parse_datetime(log_data.iloc[i]['Date'], log_data.iloc[i]['Time'])
    
    next_component = log_data.iloc[i + 1]['Component']
    next_event = log_data.iloc[i + 1]['EventId']
    next_time = parse_datetime(log_data.iloc[i + 1]['Date'], log_data.iloc[i + 1]['Time'])
    
    # 시간 차이를 초 단위로 계산
    time_difference = (next_time - current_time).total_seconds()
    
    # 시간 정보를 문자열로 변환하여 엣지 속성으로 추가
    G.add_edge(
        current_component,
        next_component,
        relation='temporal_sequence',
        content=current_content,
        time=current_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
        time_difference=time_difference
    )
    
    # EventId 간 엣지 추가 시에도 시간 정보 포함
    G.add_edge(
        current_event,
        next_event,
        relation='event_sequence',
        content=current_content,
        time=current_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
        time_difference=time_difference
    )
    
#%%
# 지식 그래프를 GEXF 파일로 저장
output_path = "./Android_Knowledge_Graph_with_time.gexf"
nx.write_gexf(G, output_path)

#-----------------------------------------------------------------------
## 지식그래프 시각화
import matplotlib.pyplot as plt

# %%
# 저장된 GEXF 파일 불러오기
graph_path = "./Android_Knowledge_Graph_with_time.gexf"
G = nx.read_gexf(graph_path)

#%%
# 단순 그래프로 변환
simple_graph = nx.DiGraph()
for u, v, data in G.edges(data=True):
    if not simple_graph.has_edge(u, v):
        simple_graph.add_edge(u, v, relation=data.get("relation", ""))

# %%
# 그래프 시각화
plt.figure(figsize=(15, 15))
pos = nx.kamada_kawai_layout(G)  # 노드 배치를 위한 레이아웃 설정

#%%
# 노드와 엣지 그리기
nx.draw(simple_graph, pos, with_labels=True, node_size=30, node_color="skyblue",
        font_size=6, font_color="darkblue", edge_color="gray", alpha=0.7)

# 엣지 라벨 표시
edge_labels = nx.get_edge_attributes(simple_graph, 'relation')
nx.draw_networkx_edge_labels(simple_graph, pos, edge_labels=edge_labels, font_size=5, alpha=0.6)

plt.title("Android User Log Knowledge Graph(Event ID, Component)")
plt.axis("off")
plt.show()
# %% [markdown]
# 1. 노드 : 안드로이드 Component 및 이벤트 ID EventID (ex.indowManager, PowerManagerService, E12)

# 2. 엣지 : 노드 간의 관계, 주로 event_sequence 관계가 포함
# event_sequence 관계는 시간 순서에 따라 발생하는 이벤트 간의 흐름을 나타냄 >> 이 관계를 통해 어떤 이벤트가 순차적으로 발생했는지, 또는 특정 구성 요소가 다른 구성 요소와 어떻게 연결되는지 알수있음
#------------------------------------------------------------------------------------------------------------------------------------------------------------
# %%
## 2. 지식그래프 구축 (time & component)

# 지식 그래프 초기화
G_2 = nx.DiGraph()

# 시간 형식 변환 함수
def parse_datetime(date_str, time_str):
    return datetime.strptime(f"{date_str} {time_str}", "%m-%d %H:%M:%S.%f")

# 로그 데이터를 순회하며 노드와 엣지 추가
for i in range(len(log_data) - 1):
    # 현재와 다음 로그 항목의 정보
    current_component = log_data.iloc[i]['Component']
    current_time = parse_datetime(log_data.iloc[i]['Date'], log_data.iloc[i]['Time'])
    
    next_component = log_data.iloc[i + 1]['Component']
    next_time = parse_datetime(log_data.iloc[i + 1]['Date'], log_data.iloc[i + 1]['Time'])
    
    # 시간 차이를 초 단위로 계산
    time_difference = (next_time - current_time).total_seconds()
    
    # 노드 추가
    G_2.add_node(current_component)
    G_2.add_node(next_component)
    
    # 시간 순서에 따른 엣지 추가
    G_2.add_edge(
        current_component,
        next_component,
        time=current_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
        time_difference=time_difference
    )

# 그래프를 GEXF 파일로 저장
output_path = "./Android_Knowledge_Graph_Time_Component_2.gexf"
nx.write_gexf(G_2, output_path)

#%%
# 시각화
graph_path = "./Android_Knowledge_Graph_Time_Component_2.gexf"
G_2 = nx.read_gexf(graph_path)

#%%
# 단순 그래프로 변환
simple_graph = nx.DiGraph()
for u, v, data in G_2.edges(data=True):
    if not simple_graph.has_edge(u, v):
        simple_graph.add_edge(u, v, relation=data.get("relation", ""))

# %%
# 그래프 시각화
plt.figure(figsize=(15, 15))
pos = nx.kamada_kawai_layout(G_2)  # 노드 배치를 위한 레이아웃 설정

#%%
# 노드와 엣지 그리기
nx.draw(simple_graph, pos, with_labels=True, node_size=30, node_color="skyblue",
        font_size=6, font_color="darkblue", edge_color="gray", alpha=0.7)

#엣지 라벨 표시
edge_labels = {(u, v): f"{data['time_difference']}s" for u, v, data in G_2.edges(data=True)}
nx.draw_networkx_edge_labels(G_2, pos, edge_labels=edge_labels, font_size=7, label_pos=0.5)

plt.title("Android User Log Knowledge Graph (Time and Component)")
plt.axis("off")
plt.show()

#-----------------------------------------------------------------------------------------------------
# %% [markdown]
## 3. 프로세스 마이닝 모델과 결합하기 쉽도록 지식그래프 구축
### 이벤트간 흐름 및 프로세스 흐름 엣지로 추가 / 노드는 이벤트 및 프로세스 단계로 분리
### => EventId, ProcessStep을 노드로 하고, 각 이벤트와 프로세스 단계 간의 관계를 시각화
#%%

# 지식 그래프 초기화
G_3 = nx.DiGraph()

#%%
# 시간 형식 변환 함수
def parse_datetime(date_str, time_str):
    return datetime.strptime(f"{date_str} {time_str}", "%m-%d %H:%M:%S.%f")

# 로그 데이터를 순회하며 노드와 엣지 추가
for i in range(len(log_data) - 1):
    # 현재와 다음 로그 항목의 정보
    current_component = log_data.iloc[i]['Component']
    current_event = log_data.iloc[i]['EventId']
    current_time = parse_datetime(log_data.iloc[i]['Date'], log_data.iloc[i]['Time'])
    
    next_component = log_data.iloc[i + 1]['Component']
    next_event = log_data.iloc[i + 1]['EventId']
    next_time = parse_datetime(log_data.iloc[i + 1]['Date'], log_data.iloc[i + 1]['Time'])
    
    # 시간 차이를 초 단위로 계산
    time_difference = (next_time - current_time).total_seconds()
    
    # 노드 추가 (이벤트 및 프로세스 단계로 분리)
    G_3.add_node(current_event, type='Event', component=current_component)
    G_3.add_node(f"Process_{current_event}", type='ProcessStep', component=current_component)
    
    # 이벤트 간 흐름을 나타내는 엣지 추가
    G_3.add_edge(current_event, next_event, relation='follows', time_difference=time_difference)
    # 프로세스 단계 간 흐름을 나타내는 엣지 추가
    G_3.add_edge(f"Process_{current_event}", f"Process_{next_event}", relation='follows', time_difference=time_difference)
#%%
# 지식 그래프를 GEXF 파일로 저장
output_path = "./Process_Knowledge_Graph.gexf"
nx.write_gexf(G_3, output_path)

#%%

# 그래프 시각화
plt.figure(figsize=(15, 15))
pos = nx.spring_layout(G_3, seed=42)  # 레이아웃 설정

#%%
# 노드 스타일 설정
node_colors = []
node_labels = {}
for node, data in G_3.nodes(data=True):
    if data['type'] == 'Event':
        node_colors.append("skyblue")
        node_labels[node] = f"Event {node}"  # Event 노드 라벨
    elif data['type'] == 'ProcessStep':
        node_colors.append("lightgreen")
        node_labels[node] = f"Process {node}"  # ProcessStep 노드 라벨

#%%
# 노드 그리기
nx.draw_networkx_nodes(G_3, pos, node_color=node_colors, node_size=100, alpha=0.8)

# 엣지 스타일 설정 및 그리기
nx.draw_networkx_edges(G_3, pos, edge_color="gray", alpha=0.3, arrows=True)

# 노드 라벨 표시
nx.draw_networkx_labels(G_3, pos, labels=node_labels, font_size=8, font_color="darkblue")

# 엣지 라벨 표시 (시간 차이 정보)
edge_labels = {(u, v): f"{data['time_difference']}s" for u, v, data in G_3.edges(data=True)}
nx.draw_networkx_edge_labels(G_3, pos, edge_labels=edge_labels, font_size=7, label_pos=0.5)

plt.title("Process Knowledge Graph (Event and Process Steps)")
plt.axis("off")
plt.show()


# %%
# 그래프 더 잘보이도록!!
# 노드와 엣지 필터링 설정 (예: 상위 20개의 Event와 ProcessStep만 표시)
top_events = [node for node, data in G_3.nodes(data=True) if data['type'] == 'Event'][:20]
top_process_steps = [node for node, data in G_3.nodes(data=True) if data['type'] == 'ProcessStep'][:20]
subgraph_nodes = top_events + top_process_steps
H = G_3.subgraph(subgraph_nodes)  # 서브그래프 생성

# 시각화
plt.figure(figsize=(15, 15))
pos = nx.kamada_kawai_layout(H)  # 노드를 고르게 배치하는 레이아웃 사용

# 노드 스타일 설정
node_colors = []
node_labels = {}
for node, data in H.nodes(data=True):
    if data['type'] == 'Event':
        node_colors.append("skyblue")
        node_labels[node] = f"Event {node}"
    elif data['type'] == 'ProcessStep':
        node_colors.append("lightgreen")
        node_labels[node] = f"Process {node}"

# 노드와 엣지 그리기
nx.draw_networkx_nodes(H, pos, node_color=node_colors, node_size=80, alpha=0.8)
nx.draw_networkx_edges(H, pos, edge_color="gray", alpha=0.3, arrows=True)
nx.draw_networkx_labels(H, pos, labels=node_labels, font_size=8, font_color="darkblue")

# 엣지 라벨 표시 (필요할 경우만 활성화)
edge_labels = {(u, v): f"{data['time_difference']}s" for u, v, data in H.edges(data=True)}
nx.draw_networkx_edge_labels(H, pos, edge_labels=edge_labels, font_size=7, label_pos=0.5)

plt.title("Filtered Process Knowledge Graph (Top Events and Process Steps)")
plt.axis("off")
plt.show()
# %%
