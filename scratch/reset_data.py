"""
Boardroom AI -- One-Click Dataset Reset and Generation Script
=============================================================
Clears the existing database and CSV files, then generates 5 fresh,
realistic enterprise-grade dummy datasets spanning Jan 2024 to May 2026
(historical) and Jun 2026 to May 2027 (forecast).

Run from the boardroom-ai/ project root:
    uv run python scratch/reset_data.py
"""

import sys
import os
import sqlite3
import shutil
import uuid
import random
import datetime
import csv
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Path Setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR   = PROJECT_ROOT / "data"
UPLOAD_DIR = PROJECT_ROOT / "backend" / "uploads"
DB_PATH    = PROJECT_ROOT / "backend" / "datasets.db"

print("=" * 70)
print("  BOARDROOM AI -- Dataset Reset and Generation Script")
print("=" * 70)

# ---------------------------------------------------------------------------
# STEP 1 -- Delete old CSVs in data/
# ---------------------------------------------------------------------------
print("\n[1/7] Deleting old CSV files in data/ ...")
DATA_DIR.mkdir(parents=True, exist_ok=True)
deleted = 0
for f in DATA_DIR.glob("*.csv"):
    f.unlink()
    print(f"      Deleted: {f.name}")
    deleted += 1
print(f"      -> {deleted} file(s) deleted.")

# ---------------------------------------------------------------------------
# STEP 2 -- Delete all files in backend/uploads/
# ---------------------------------------------------------------------------
print("\n[2/7] Clearing backend/uploads/ ...")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
deleted = 0
for f in UPLOAD_DIR.iterdir():
    if f.is_file():
        f.unlink()
        deleted += 1
print(f"      -> {deleted} upload file(s) deleted.")

# ---------------------------------------------------------------------------
# STEP 3 -- Clear SQLite database tables
# ---------------------------------------------------------------------------
print("\n[3/7] Clearing SQLite database tables ...")
TABLES_TO_CLEAR = [
    "datasets","investigations","working_memory","episodic_memory",
    "semantic_memory","skills","agent_runs","security_events",
    "evaluations","observability_metrics"
]
if DB_PATH.exists():
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    cursor = conn.cursor()
    for table in TABLES_TO_CLEAR:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"      Cleared table: {table}")
        except Exception as e:
            print(f"      (Skipped {table}: {e})")
    conn.commit()
    conn.close()
    print("      -> SQLite tables cleared.")
else:
    print("      -> No SQLite database found (will be created on first run).")

# ---------------------------------------------------------------------------
# STEP 4 -- Clear Supabase datasets table (optional best-effort)
# ---------------------------------------------------------------------------
print("\n[4/7] Attempting to clear Supabase datasets table (optional) ...")
try:
    from backend.database.supabase import supabase_client
    if supabase_client:
        supabase_client.table("datasets").delete().neq("id","00000000-0000-0000-0000-000000000000").execute()
        print("      -> Supabase datasets table cleared.")
    else:
        print("      -> Supabase not active. Skipping.")
except Exception as e:
    print(f"      -> Supabase clear failed (non-critical): {e}")

# ---------------------------------------------------------------------------
# Helper Utilities
# ---------------------------------------------------------------------------
random.seed(42)

REGIONS  = ["North","South","East","West","Central"]
PRODUCTS = [
    ("P001","CloudSync Pro","SaaS"),
    ("P002","DataVault Enterprise","SaaS"),
    ("P003","NetShield Plus","Security"),
    ("P004","AnalyticsEdge","SaaS"),
    ("P005","ConnectBridge","Integration"),
    ("P006","StorageMax HDD","Hardware"),
    ("P007","ServerLink X1","Hardware"),
    ("P008","CyberAudit Suite","Security"),
    ("P009","WorkflowPro","SaaS"),
    ("P010","InsightDash","Analytics"),
    ("P011","APIGateway Pro","Integration"),
    ("P012","BackupCloud Ultra","SaaS"),
]
CHANNELS = ["Direct","Online","Partner","Enterprise"]
MANAGERS = {
    "North":"Sarah Mitchell","South":"James Rivera","East":"Priya Nair",
    "West":"David Chen","Central":"Aisha Thompson",
}

def months_range(sy,sm,ey,em):
    y,m=sy,sm
    while (y,m)<=(ey,em):
        yield (y,m)
        m+=1
        if m>12:
            m=1;y+=1

SEASONALITY={1:0.88,2:0.85,3:0.95,4:0.98,5:0.92,6:1.02,
             7:0.90,8:0.91,9:1.05,10:1.08,11:1.18,12:1.25}

BUSINESS_EVENTS={
    (2024,10,"ALL",None):  ("Pre-holiday stocking surge","holiday_spike",None,1.10),
    (2024,11,"ALL",None):  ("Black Friday enterprise deals","holiday_spike",None,1.20),
    (2024,12,"ALL",None):  ("Year-end budget flush","holiday_spike",None,1.28),
    (2025,2,"East",None):  ("Competitor product launch in East","competitor_launch","warning",0.88),
    (2025,3,"West",None):  ("Google Ads campaign success","marketing_success",None,1.18),
    (2025,4,"North",None): ("Seasonal SaaS renewal slowdown","regional_slowdown","warning",0.91),
    (2025,5,"North",None): ("Seasonal SaaS renewal slowdown","regional_slowdown","warning",0.90),
    (2025,6,"North",None): ("Partial SaaS recovery","regional_recovery",None,0.96),
    (2025,8,"East","P004"):  ("Supplier delay AnalyticsEdge","supplier_delay","warning",0.82),
    (2025,8,"Central","P004"):("Supplier delay AnalyticsEdge","supplier_delay","warning",0.83),
    (2025,10,"ALL",None):  ("Pre-holiday enterprise stocking","holiday_spike",None,1.12),
    (2025,11,"ALL",None):  ("Black Friday + year-end push","holiday_spike",None,1.22),
    (2025,12,"ALL",None):  ("Year-end budget allocation","holiday_spike",None,1.30),
    (2026,1,"South",None): ("New enterprise contracts signed","enterprise_expansion",None,1.22),
    (2026,3,"East",None):  ("Competitor aggressive promotion","competitor_promotion","warning",0.88),
    (2026,4,"East","P002"): ("Supplier delay DataVault East WH","supplier_delay","warning",0.75),
    (2026,5,"East","P002"): ("Stockout DataVault East WH","supplier_delay","critical",0.35),
    (2026,5,"East",None):  ("Revenue crash stockout + churn","critical_event","critical",0.60),
}

def get_event(year,month,region,pid):
    for key in [(year,month,region,pid),(year,month,region,None),(year,month,"ALL",None)]:
        if key in BUSINESS_EVENTS:
            return BUSINESS_EVENTS[key]
    return (None,None,None,1.0)

BASE_PRICES={"P001":299,"P002":549,"P003":189,"P004":399,"P005":249,
             "P006":899,"P007":1299,"P008":459,"P009":199,"P010":349,
             "P011":279,"P012":149}
BASE_COSTS_PCT={"P001":0.35,"P002":0.38,"P003":0.30,"P004":0.40,"P005":0.32,
                "P006":0.55,"P007":0.60,"P008":0.28,"P009":0.33,"P010":0.37,
                "P011":0.31,"P012":0.29}

# ---------------------------------------------------------------------------
# STEP 5 -- Generate CSV files
# ---------------------------------------------------------------------------
print("\n[5/7] Generating dataset files ...")

# ---- sales_large.csv ----
print("      Generating sales_large.csv ...")
HISTORICAL_MONTHS=list(months_range(2024,1,2026,5))
sales_rows=[]
for (year,month) in HISTORICAL_MONTHS:
    season_mult=SEASONALITY[month]
    ym_str=f"{year}-{month:02d}-01"
    for region in REGIONS:
        for (pid,pname,category) in PRODUCTS:
            ev_desc,ev_type,anomaly,ev_mult=get_event(year,month,region,pid)
            if ev_mult==1.0:
                _,_,_,ev_mult2=get_event(year,month,region,None)
                if ev_mult2!=1.0:
                    ev_mult=ev_mult2
                    ev_desc,ev_type,anomaly,_=get_event(year,month,region,None)
            noise=random.uniform(0.95,1.05)
            base_units=random.randint(80,420)
            unit_price=BASE_PRICES[pid]*random.uniform(0.95,1.08)
            discount=round(random.uniform(0.03,0.20),2)
            units_sold=max(1,int(base_units*season_mult*ev_mult*noise))
            revenue=round(units_sold*unit_price*(1-discount),2)
            cost=round(revenue*BASE_COSTS_PCT[pid],2)
            profit=round(revenue-cost,2)
            channel=random.choice(CHANNELS)
            manager=MANAGERS[region]
            sales_rows.append({
                "date":ym_str,"region":region,"product_id":pid,
                "product_name":pname,"category":category,
                "units_sold":units_sold,"unit_price":round(unit_price,2),
                "discount":discount,"revenue":revenue,"cost":cost,"profit":profit,
                "sales_channel":channel,"sales_manager":manager,
                "event":ev_desc or "","event_type":ev_type or "","anomaly":anomaly or "",
            })
sales_path=DATA_DIR/"sales_large.csv"
with open(sales_path,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(sales_rows[0].keys()));w.writeheader();w.writerows(sales_rows)
print(f"      -> sales_large.csv: {len(sales_rows):,} rows written.")

# ---- customers_large.csv ----
print("      Generating customers_large.csv ...")
FIRST_NAMES=["Alice","Bob","Carlos","Diana","Ethan","Fiona","George","Hannah","Ivan","Julia",
             "Kevin","Laura","Michael","Nina","Oscar","Paula","Quinn","Rachel","Steve","Tina",
             "Umar","Vera","William","Xena","Yusuf","Zara","Aaron","Beth","Chloe","Derek"]
LAST_NAMES=["Smith","Patel","Johnson","Lee","Garcia","Kim","Nguyen","Brown","Davis","Wilson",
            "Martinez","Anderson","Taylor","Thomas","Jackson","White","Harris","Martin","Thompson","Robinson"]
COMPANIES=["Acme Corp","TechVentures","GlobalRetail","NexGen Systems","AlphaCo","BlueOcean Inc",
           "PrimeSoft","GreenField Ltd","OmniCorp","StarLink Technologies","DataBridge","ClearPath"]
SEGMENTS=["Enterprise","Premium","Standard"]
SEG_WEIGHTS=[0.20,0.35,0.45]

def should_churn(segment,region):
    base={"Enterprise":0.04,"Premium":0.10,"Standard":0.16}[segment]
    spike=0.0
    if segment=="Premium" and region=="East": spike=0.20
    elif segment=="Standard" and region in ["East","Central"]: spike=0.10
    return random.random()<min(0.90,base+spike)

customer_rows=[]
for i in range(1,1001):
    cid=f"C{i:04d}"
    name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    company=random.choice(COMPANIES)
    region=random.choice(REGIONS)
    segment=random.choices(SEGMENTS,weights=SEG_WEIGHTS)[0]
    signup_yr=random.randint(2022,2024);signup_mo=random.randint(1,12)
    signup_date=f"{signup_yr}-{signup_mo:02d}-{random.randint(1,28):02d}"
    last_yr=random.randint(signup_yr,2026)
    last_mo=random.randint(1,5) if last_yr==2026 else random.randint(1,12)
    last_purchase=f"{last_yr}-{last_mo:02d}-{random.randint(1,28):02d}"
    ltv=round(random.uniform(5000,250000),2)
    orders=random.randint(3,120)
    satisfaction=round(random.uniform(2.5,5.0),1)
    loyalty=random.randint(15,100)
    churned=should_churn(segment,region)
    churn_month=""
    if churned:
        if segment=="Premium" and region=="East":
            churn_month="2026-05"
        else:
            cyr=random.randint(2024,2026)
            cmo=random.randint(1,5) if cyr==2026 else random.randint(1,12)
            churn_month=f"{cyr}-{cmo:02d}"
    customer_rows.append({
        "customer_id":cid,"customer_name":name,"company":company,"region":region,
        "segment":segment,"signup_date":signup_date,"last_purchase":last_purchase,
        "lifetime_value":ltv,"total_orders":orders,"satisfaction_score":satisfaction,
        "loyalty_score":loyalty,"churned":"Yes" if churned else "No","churn_month":churn_month,
    })
cust_path=DATA_DIR/"customers_large.csv"
with open(cust_path,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(customer_rows[0].keys()));w.writeheader();w.writerows(customer_rows)
print(f"      -> customers_large.csv: {len(customer_rows):,} rows written.")

# ---- forecast_enterprise.csv ----
print("      Generating forecast_enterprise.csv ...")
FORECAST_MONTHS=list(months_range(2026,6,2027,5))
hist_rev=defaultdict(list)
for row in sales_rows:
    hist_rev[(row["region"],row["product_id"])].append(row["revenue"])
def avg(lst): return sum(lst)/len(lst) if lst else 50000.0
FORECAST_REASONS=[
    "Post-Q2 recovery driven by H2 seasonality",
    "Expected recovery following May 2026 stockout resolution",
    "Enterprise contract renewals projected in Q3",
    "Back-to-school and IT procurement cycle",
    "Holiday budget allocation expected to boost sales",
    "YoY growth trajectory maintained from 2025 H2",
    "Supplier delay resolved -- full inventory restored",
    "Marketing campaigns scheduled for Q4 2026",
    "Conservative estimate pending East region recovery",
    "Optimistic estimate based on South expansion momentum",
]
forecast_rows=[]
for (year,month) in FORECAST_MONTHS:
    season_mult=SEASONALITY[month]
    fm_str=f"{year}-{month:02d}"
    for region in REGIONS:
        for (pid,pname,_cat) in PRODUCTS:
            baseline=avg(hist_rev[(region,pid)])
            noise=random.uniform(0.97,1.03)
            pred_rev=round(baseline*season_mult*1.03*noise,2)
            if region=="East" and year==2026 and month>=7:
                pred_rev=round(pred_rev*1.15,2)
            pred_profit=round(pred_rev*(1-BASE_COSTS_PCT[pid]),2)
            growth_pct=round(random.uniform(2.5,14.5),1)
            confidence=random.randint(72,97)
            lower=round(pred_rev*0.90,2);upper=round(pred_rev*1.10,2)
            reason=random.choice(FORECAST_REASONS)
            forecast_rows.append({
                "forecast_month":fm_str,"region":region,"product_id":pid,"product":pname,
                "predicted_revenue":pred_rev,"predicted_profit":pred_profit,
                "growth_percent":growth_pct,"confidence":confidence,
                "lower_bound":lower,"upper_bound":upper,"forecast_reason":reason,
            })
fore_path=DATA_DIR/"forecast_enterprise.csv"
with open(fore_path,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(forecast_rows[0].keys()));w.writeheader();w.writerows(forecast_rows)
print(f"      -> forecast_enterprise.csv: {len(forecast_rows):,} rows written.")

# ---- inventory_large.csv ----
print("      Generating inventory_large.csv ...")
SUPPLIERS=["GlobalParts Inc","TechSupply Ltd","EastWest Logistics","NovaBridge Supplies",
           "CoreComponents","SwiftParts Co","AlphaSupplier","DigiStock Hub"]
STOCKOUT_MAP={
    ("DataVault Enterprise","East","2026-04"):("GlobalParts Inc",28,"Yes","2026-04","Supplier delayed Q2 2026 shipment by 28 days"),
    ("DataVault Enterprise","East","2026-05"):("GlobalParts Inc",42,"Yes","2026-05","Critical stockout -- no inventory in East WH"),
    ("AnalyticsEdge","East","2025-08"):("CoreComponents",18,"Yes","2025-08","Supplier delay -- partial stockout Aug 2025"),
    ("AnalyticsEdge","Central","2025-08"):("CoreComponents",18,"Yes","2025-08","Supplier delay -- partial stockout Aug 2025"),
}
inventory_rows=[];sku_counter=1
for (pid,pname,_cat) in PRODUCTS:
    for region in REGIONS:
        for _ in range(random.randint(3,5)):
            sku_id=f"SKU{sku_counter:05d}";sku_counter+=1
            key=(pname,region,"2026-05")
            if key in STOCKOUT_MAP:
                supplier,lead,stockout,sm,note=STOCKOUT_MAP[key]
                stock=random.randint(0,15);reorder=random.randint(100,200)
            else:
                supplier=random.choice(SUPPLIERS);lead=random.randint(5,30)
                stockout="No";sm="";note=""
                stock=random.randint(50,4000);reorder=random.randint(50,500)
            inventory_rows.append({
                "sku":sku_id,"product_id":pid,"product":pname,"warehouse":region,"region":region,
                "stock":stock,"reorder_level":reorder,"supplier":supplier,"lead_time_days":lead,
                "stockout":stockout,"stockout_month":sm,"event_note":note,
            })
while len(inventory_rows)<1000:
    pid2,pname2,_=random.choice(PRODUCTS);region2=random.choice(REGIONS)
    inventory_rows.append({
        "sku":f"SKU{sku_counter:05d}","product_id":pid2,"product":pname2,
        "warehouse":region2,"region":region2,"stock":random.randint(100,3000),
        "reorder_level":random.randint(50,400),"supplier":random.choice(SUPPLIERS),
        "lead_time_days":random.randint(5,25),"stockout":"No","stockout_month":"","event_note":"",
    });sku_counter+=1
inv_path=DATA_DIR/"inventory_large.csv"
with open(inv_path,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(inventory_rows[0].keys()));w.writeheader();w.writerows(inventory_rows[:1000])
print(f"      -> inventory_large.csv: 1,000 rows written.")

# ---- marketing_large.csv ----
print("      Generating marketing_large.csv ...")
CHANNELS_MKT=["Google Ads","Meta Ads","LinkedIn","Email","Events","Webinar","Content Marketing"]
CAMPAIGN_PREFIXES=["Q1","Q2","Q3","Q4","Holiday","Seasonal","Enterprise","SMB","Brand",
                   "Product Launch","Retargeting","Awareness","Conversion","Regional"]
marketing_rows=[]
for i in range(1,501):
    cmp_id=f"CMP{i:03d}";region=random.choice(REGIONS);channel=random.choice(CHANNELS_MKT)
    yr=random.randint(2024,2026);mo=random.randint(1,5) if yr==2026 else random.randint(1,12)
    cmo=f"{yr}-{mo:02d}";sday=random.randint(1,15);eday=min(sday+random.randint(7,21),28)
    c_start=f"{yr}-{mo:02d}-{sday:02d}";c_end=f"{yr}-{mo:02d}-{eday:02d}"
    cmp_name=f"{random.choice(CAMPAIGN_PREFIXES)} {yr} -- {channel} ({region})"
    budget=round(random.uniform(5000,100000),2);spend=round(budget*random.uniform(0.75,1.00),2)
    clicks=random.randint(200,45000);conv_rate=random.uniform(0.02,0.18)
    conversions=max(1,int(clicks*conv_rate));rev_per_conv=random.uniform(150,2500)
    rev_attributed=round(conversions*rev_per_conv,2)
    roi=round((rev_attributed-spend)/spend*100,1)
    if region=="East" and yr==2026 and mo in [4,5]:
        spend=round(spend*0.55,2);rev_attributed=round(rev_attributed*0.60,2)
        roi=round((rev_attributed-spend)/spend*100,1)
    marketing_rows.append({
        "campaign_id":cmp_id,"campaign_name":cmp_name,"channel":channel,"region":region,
        "budget":budget,"spend":spend,"clicks":clicks,"conversions":conversions,
        "revenue_attributed":rev_attributed,"roi":roi,
        "campaign_start":c_start,"campaign_end":c_end,"campaign_month":cmo,
    })
mkt_path=DATA_DIR/"marketing_large.csv"
with open(mkt_path,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(marketing_rows[0].keys()));w.writeheader();w.writerows(marketing_rows)
print(f"      -> marketing_large.csv: {len(marketing_rows):,} rows written.")

# ---------------------------------------------------------------------------
# STEP 6 -- Reinitialize database schema
# ---------------------------------------------------------------------------
print("\n[6/7] Reinitializing database schema ...")
try:
    from backend.database.supabase import db_init
    db_init()
    print("      -> Database schema initialized.")
except Exception as e:
    print(f"      -> db_init failed: {e}")

# ---------------------------------------------------------------------------
# STEP 7 -- Seed all 5 CSV files into the database
# ---------------------------------------------------------------------------
print("\n[7/7] Seeding datasets into the database ...")
CSV_FILES=[sales_path,cust_path,fore_path,inv_path,mkt_path]
try:
    from backend.services.dataset_service import create_dataset
    for csv_file in CSV_FILES:
        with open(csv_file,"rb") as f: content=f.read()
        did=create_dataset(csv_file.name,content)
        print(f"      Seeded: {csv_file.name} -> ID: {did}")
except Exception as e:
    print(f"      Service seeding failed: {e}\n      Falling back to direct SQLite insert ...")
    conn=sqlite3.connect(str(DB_PATH),timeout=30.0);cursor=conn.cursor()
    now=datetime.datetime.utcnow().isoformat()
    for csv_file in CSV_FILES:
        dest=UPLOAD_DIR/f"{uuid.uuid4().hex}_{csv_file.name}";shutil.copy(str(csv_file),str(dest))
        did=str(uuid.uuid4())
        cursor.execute("INSERT OR IGNORE INTO datasets (id,name,uploaded_at,file_path) VALUES (?,?,?,?)",(did,csv_file.name,now,str(dest)))
        print(f"      Seeded: {csv_file.name} -> ID: {did}")
    conn.commit();conn.close()

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n"+"="*70)
print("  RESET COMPLETE")
print("="*70)
print(f"  Data files in:  {DATA_DIR}")
print(f"  Database:       {DB_PATH}")
print(f"  Uploads dir:    {UPLOAD_DIR}")
print()
print("  Files generated:")
print(f"    sales_large.csv          -- {len(sales_rows):,} rows (Jan 2024 to May 2026)")
print(f"    customers_large.csv      -- {len(customer_rows):,} rows")
print(f"    forecast_enterprise.csv  -- {len(forecast_rows):,} rows (Jun 2026 to May 2027)")
print(f"    inventory_large.csv      -- 1,000 rows")
print(f"    marketing_large.csv      -- {len(marketing_rows):,} rows")
print()
print("  Key embedded business events:")
print("    Q4 2024  : Holiday spike (+25-28%) all regions")
print("    Feb 2025 : Competitor launch East (-12%)")
print("    Mar 2025 : Marketing success West (+18%)")
print("    Q2 2025  : North seasonal slowdown (-8 to -10%)")
print("    Aug 2025 : Supplier delay East+Central AnalyticsEdge (-15%)")
print("    Q4 2025  : Holiday spike (+28-30%) all regions")
print("    Jan 2026 : Enterprise expansion South (+22%)")
print("    Mar 2026 : Competitor promotion East (-10%)")
print("    Apr 2026 : Supplier delay East DataVault (-25%)")
print("    May 2026 : CRITICAL CRASH East DataVault stockout (-38%)")
print("    May 2026 : Premium churn spike East (customers_large.csv)")
print()
print("  Next step: Open the Streamlit dashboard at http://localhost:8501")
print("  and verify all 5 datasets appear in the Dataset Explorer.")
print("="*70)
