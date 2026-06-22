import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import ReactECharts from "echarts-for-react";
import { ArrowsClockwise, Books, ChartLineUp, Database, Flask, GitBranch, House, Play, Pulse, Scales, Strategy, Warning } from "@phosphor-icons/react";
import { api, Result, Run } from "./api/client";

type Page = "overview" | "strategies" | "builder" | "runs" | "compare" | "experiments" | "data";
const symbols = ["510300", "510500", "512100", "512480", "512690", "515000"];
const nav: Array<[Page, string, typeof House]> = [
  ["overview", "研究总览", House], ["strategies", "策略库", Books], ["builder", "回测构建", Play],
  ["runs", "运行记录", Pulse], ["compare", "策略比较", Scales], ["experiments", "实验登记", Flask], ["data", "数据目录", Database]
];
const fmt = (value = 0, percent = true) => percent ? `${(value * 100).toFixed(2)}%` : value.toFixed(2);

function Metric({label, value, tone}: {label: string; value: string; tone?: "cyan" | "coral"}) {
  return <div className={`metric ${tone ?? ""}`}><span>{label}</span><strong>{value}</strong></div>;
}

function EquityChart({result, title = "净值与回撤"}: {result?: Result; title?: string}) {
  const dates = result?.equity.map(row => row.date) ?? [];
  return <section className="panel chart-panel"><header><div><small>PERFORMANCE</small><h3>{title}</h3></div><span className="legend">净值 / 回撤</span></header><ReactECharts style={{height: 310}} option={{
    backgroundColor: "transparent", tooltip: {trigger: "axis"}, legend: {show: false}, grid: {left: 48, right: 22, top: 24, bottom: 42},
    xAxis: {type: "category", data: dates, axisLabel: {color: "#758094", hideOverlap: true}, axisLine: {lineStyle: {color: "#263246"}}},
    yAxis: [{type: "value", axisLabel: {color: "#758094"}, splitLine: {lineStyle: {color: "#1e293a"}}}, {type: "value", axisLabel: {formatter: "{value}%", color: "#758094"}, splitLine: {show: false}}],
    series: [{type: "line", data: result?.equity.map(r => r.equity), smooth: true, symbol: "none", lineStyle: {width: 2, color: "#37d6cf"}, areaStyle: {color: "rgba(55,214,207,.10)"}},
      {type: "line", yAxisIndex: 1, data: result?.equity.map(r => r.drawdown * 100), symbol: "none", lineStyle: {color: "#ff785f", width: 1}, areaStyle: {color: "rgba(255,120,95,.08)"}}]
  }} /></section>;
}

function App() {
  const [page, setPage] = useState<Page>("overview");
  const [selectedRun, setSelectedRun] = useState<string>("");
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const qc = useQueryClient();
  const strategies = useQuery({queryKey: ["strategies"], queryFn: api.strategies});
  const runs = useQuery({queryKey: ["runs"], queryFn: api.runs});
  const snapshots = useQuery({queryKey: ["snapshots"], queryFn: api.snapshots});
  const experiments = useQuery({queryKey: ["experiments"], queryFn: api.experiments});
  const completed = runs.data?.filter(run => run.status === "completed") ?? [];
  const activeRun = selectedRun || completed[0]?.id;
  const activeRecord = runs.data?.find(run => run.id === activeRun);
  const result = useQuery({queryKey: ["result", activeRun], queryFn: () => api.result(activeRun), enabled: activeRecord?.status === "completed"});

  return <div className="shell"><aside><div className="brand"><div className="brand-mark"><Strategy size={21}/></div><div><b>策略图谱</b><span>QUANT RESEARCH</span></div></div><nav>{nav.map(([id,label,Icon]) => <button key={id} className={page === id ? "active" : ""} onClick={() => setPage(id)}><Icon size={19}/><span>{label}</span></button>)}</nav><div className="rail-foot"><GitBranch size={17}/><div><b>main</b><span>可追溯工作区</span></div></div></aside>
    <main><header className="topbar"><div><small>QUANT RESEARCH PLATFORM</small><h1>{nav.find(item => item[0] === page)?.[1]}</h1></div><div className="system"><i></i><span>本地引擎</span><b>{runs.isError ? "未连接" : "在线"}</b></div></header>
      {runs.isError ? <div className="alert"><Warning size={20}/>API 尚未启动。运行 <code>./scripts/dev.ps1</code> 后刷新。</div> : null}
      <div className="content">
        {page === "overview" && <Overview runs={runs.data ?? []} result={result.data} strategies={strategies.data?.length ?? 0} snapshots={snapshots.data?.length ?? 0} onOpen={(id) => {setSelectedRun(id);setPage("runs")}} />}
        {page === "strategies" && <Strategies items={strategies.data ?? []} reload={() => api.reload().then(() => qc.invalidateQueries({queryKey:["strategies"]}))} />}
        {page === "builder" && <Builder onCreated={(id) => {setSelectedRun(id); setPage("runs"); qc.invalidateQueries({queryKey:["runs"]})}} />}
        {page === "runs" && <Runs runs={runs.data ?? []} selected={activeRun} select={setSelectedRun} result={activeRecord?.status === "completed" ? result.data : undefined} />}
        {page === "compare" && <Compare runs={completed} selected={compareIds} setSelected={setCompareIds} />}
        {page === "experiments" && <Experiments items={experiments.data ?? []} runs={completed} refresh={() => qc.invalidateQueries({queryKey:["experiments"]})} />}
        {page === "data" && <DataCatalog items={snapshots.data ?? []} />}
      </div>
    </main></div>;
}

function Overview({runs,result,strategies,snapshots,onOpen}: {runs:Run[];result?:Result;strategies:number;snapshots:number;onOpen:(id:string)=>void}) {
  return <><div className="metric-grid"><Metric label="策略插件" value={String(strategies)} tone="cyan"/><Metric label="冻结快照" value={String(snapshots)}/><Metric label="已完成运行" value={String(runs.filter(r=>r.status==="completed").length)}/><Metric label="最新 Sharpe" value={fmt(result?.metrics.sharpe, false)} tone="coral"/></div><div className="dashboard-grid"><EquityChart result={result}/><section className="panel lineage"><header><div><small>LINEAGE</small><h3>最近研究运行</h3></div></header>{runs.slice(0,6).map(run=><button key={run.id} onClick={()=>onOpen(run.id)}><span className={`status ${run.status}`}></span><div><b>{run.id}</b><small>{String(run.request.strategy_id)} · {new Date(run.created_at).toLocaleString("zh-CN")}</small></div><em>{run.status}</em></button>)}{!runs.length&&<p className="empty">尚无运行，从“回测构建”开始。</p>}</section></div></>;
}

function Strategies({items,reload}:{items:Awaited<ReturnType<typeof api.strategies>>;reload:()=>void}) {return <><div className="section-actions"><p>策略源代码通过 Git 审查；界面只读取清单与参数。</p><button className="secondary" onClick={reload}><ArrowsClockwise size={17}/>重新加载</button></div><div className="card-grid">{items.map(item=><article className="strategy-card" key={item.id}><div className="card-icon"><ChartLineUp size={24}/></div><span className={`pill ${item.status}`}>{item.status}</span><h3>{item.name}</h3><code>{item.id}@{item.version}</code><p>{item.description}</p><footer><span>默认现金缓冲 {item.parameters.cash_buffer?.default ?? 0}</span><span>{item.risk_notice}</span></footer></article>)}</div></>}

function Builder({onCreated}:{onCreated:(id:string)=>void}) {const [frequency,setFrequency]=useState("month_end");const [cost,setCost]=useState(10);const [cash,setCash]=useState(0);const mutation=useMutation({mutationFn:()=>api.createRun({strategy_id:"equal_weight",strategy_version:"1.0.0",parameters:{cash_buffer:cash/100},snapshot_id:"demo-cn-etf-synthetic-v1",symbols,start:"2021-01-01",end:"2025-12-31",initial_capital:1000000,rebalance:frequency,commission_bps:cost/2,slippage_bps:cost/2,t_plus_one:true,seed:42}),onSuccess:r=>onCreated(r.run_id)});return <div className="builder-grid"><section className="panel form-panel"><header><div><small>BACKTEST REQUEST</small><h3>等权链路验收</h3></div></header><label>策略<select><option>等权基准 · 1.0.0</option></select></label><label>数据快照<select><option>demo-cn-etf-synthetic-v1</option></select></label><div className="row"><label>开始日期<input value="2021-01-01" readOnly/></label><label>结束日期<input value="2025-12-31" readOnly/></label></div><label>调仓周期<select value={frequency} onChange={e=>setFrequency(e.target.value)}><option value="month_end">月末</option><option value="weekly">周频</option><option value="daily">日频压力测试</option></select></label><label>双边成本（bp）<input type="number" value={cost} onChange={e=>setCost(Number(e.target.value))}/></label><label>现金缓冲（%）<input type="number" value={cash} onChange={e=>setCash(Number(e.target.value))}/></label><div className="constraint"><b>T+1 已启用</b><span>信号于 t 产生，目标权重在 t+1 收盘成交。</span></div><button className="primary" disabled={mutation.isPending} onClick={()=>mutation.mutate()}><Play weight="fill"/>{mutation.isPending?"正在提交":"运行回测"}</button>{mutation.error&&<p className="error">{mutation.error.message}</p>}</section><section className="panel explainer"><small>REPRODUCIBILITY</small><h3>本次运行会冻结什么？</h3><ol><li><b>请求配置</b><span>策略版本、区间、成本、T+1、随机种子。</span></li><li><b>数据身份</b><span>快照 ID 与 SHA256，而不是模糊的“最新数据”。</span></li><li><b>代码身份</b><span>Git commit 与完整结果文件。</span></li><li><b>交易证据</b><span>净值、回撤、目标权重与逐笔变动。</span></li></ol></section></div>}

function Runs({runs,selected,select,result}:{runs:Run[];selected:string;select:(id:string)=>void;result?:Result}) {const current=runs.find(run=>run.id===selected);return <div className="runs-layout"><section className="panel run-list">{runs.map(run=><button className={selected===run.id?"selected":""} key={run.id} onClick={()=>select(run.id)}><span className={`status ${run.status}`}></span><div><b>{run.id}</b><small>{String(run.request.strategy_id)} · {run.status}</small></div></button>)}</section><div className="run-detail">{result?<><div className="metric-grid compact"><Metric label="累计收益" value={fmt(result.metrics.total_return)} tone="cyan"/><Metric label="年化收益" value={fmt(result.metrics.cagr)}/><Metric label="Sharpe" value={fmt(result.metrics.sharpe,false)}/><Metric label="最大回撤" value={fmt(result.metrics.max_drawdown)} tone="coral"/></div><EquityChart result={result}/><section className="panel table-panel"><header><h3>最近交易</h3><span>{result.trades.length} 条</span></header><table><thead><tr><th>日期</th><th>标的</th><th>权重变化</th><th>成交价</th></tr></thead><tbody>{result.trades.slice(-8).reverse().map((t,i)=><tr key={i}><td>{t.date}</td><td>{t.symbol}</td><td>{Number(t.weight_change).toFixed(3)}</td><td>{Number(t.price).toFixed(2)}</td></tr>)}</tbody></table></section></>:<section className="panel empty">{current?`运行状态：${current.status}`:"选择一条运行查看结果。"}</section>}</div></div>}

function Compare({runs,selected,setSelected}:{runs:Run[];selected:string[];setSelected:(v:string[])=>void}) {const mutation=useMutation({mutationFn:()=>api.compare(selected)});const options=useMemo(()=>mutation.data?.runs.map((run,index)=>({name:run.run_id,type:"line",symbol:"none",data:run.equity.map(r=>r.equity),lineStyle:{color:index?"#ff785f":"#37d6cf"}}))??[],[mutation.data]);return <><section className="panel compare-picker"><header><h3>选择两个以上运行</h3><button className="primary" disabled={selected.length<2||mutation.isPending} onClick={()=>mutation.mutate()}>生成比较</button></header><div>{runs.map(run=><label key={run.id}><input type="checkbox" checked={selected.includes(run.id)} onChange={e=>setSelected(e.target.checked?[...selected,run.id]:selected.filter(id=>id!==run.id))}/><span>{run.id}</span></label>)}</div></section>{mutation.data&&<section className="panel"><ReactECharts style={{height:420}} option={{tooltip:{trigger:"axis"},legend:{textStyle:{color:"#aab4c5"}},grid:{left:48,right:24,top:58,bottom:40},xAxis:{type:"category",data:mutation.data.runs[0].equity.map(r=>r.date),axisLabel:{color:"#758094",hideOverlap:true}},yAxis:{type:"value",axisLabel:{color:"#758094"},splitLine:{lineStyle:{color:"#1e293a"}}},series:options}}/></section>}</>}

function Experiments({items,runs,refresh}:{items:Array<Record<string,unknown>>;runs:Run[];refresh:()=>void}) {const [id,setId]=useState("E001");const [question,setQuestion]=useState("示例策略是否能稳定复现完整回测链路？");const mutation=useMutation({mutationFn:()=>api.createExperiment({experiment_id:id,question,hypothesis:"相同代码、快照与配置产生相同结果",primary_change:"建立平台基线",metrics:["reproducibility","pipeline_completion"],run_ids:runs.slice(0,1).map(r=>r.id)}),onSuccess:refresh});return <div className="experiment-grid"><section className="panel form-panel"><header><h3>登记研究问题</h3></header><label>实验编号<input value={id} onChange={e=>setId(e.target.value)}/></label><label>研究问题<textarea value={question} onChange={e=>setQuestion(e.target.value)}/></label><button className="primary" onClick={()=>mutation.mutate()}>登记实验</button></section><section className="panel registry"><header><h3>实验谱系</h3></header>{items.map((item,i)=><article key={i}><b>{String(item.experiment_id)}</b><p>{String(item.question)}</p><span>{String(item.created_at)}</span></article>)}{!items.length&&<p className="empty">尚无登记实验。</p>}</section></div>}

function DataCatalog({items}:{items:Array<Record<string,unknown>>}) {return <div className="card-grid">{items.map((item,i)=><article className="strategy-card" key={i}><div className="card-icon"><Database size={24}/></div><span className="pill example">{item.synthetic?"synthetic":"frozen"}</span><h3>{String(item.name)}</h3><code>{String(item.id)}</code><p>覆盖 {String((item.coverage as Record<string,string>)?.start)} 至 {String((item.coverage as Record<string,string>)?.end)}</p><footer><span>字段：{(item.fields as string[])?.join(" / ")}</span><span className="hash">SHA256 {String(item.sha256).slice(0,16)}…</span></footer></article>)}</div>}

export default App;
