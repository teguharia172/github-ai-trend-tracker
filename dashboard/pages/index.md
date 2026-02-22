---
title: GitHub AI Trend Tracker
---

# 🚀 GitHub AI Trend Tracker

Real-time analytics on AI open source projects from GitHub.

<LastRefreshed/>

## 📊 Key Metrics

```sql repo_stats
SELECT * FROM prod_marts.dim_repositories
```

```sql language_trends
SELECT * FROM prod_marts.fct_language_trends
```

```sql trending_repos
SELECT * FROM prod_marts.fct_trending_repos
```

<Grid cols=4>

<BigValue 
  data={repo_stats} 
  value=stars_count 
  agg=sum 
  title="Total Stars" 
/>

<BigValue 
  data={repo_stats} 
  value=repo_id 
  agg=count 
  title="Repositories" 
/>

<BigValue 
  data={repo_stats} 
  value=primary_language 
  agg=count_distinct 
  title="Languages" 
/>

<BigValue 
  data={repo_stats} 
  value=forks_count 
  agg=sum 
  title="Total Forks" 
/>

</Grid>

---

## 🌟 Top AI Repositories by Stars

<DataTable 
  data={repo_stats} 
  rows=20 
  sortable=true
  search=true
>
  <Column id=full_name title="Repository" link=html_url />
  <Column id=primary_language title="Language" />
  <Column id=stars_count title="Stars" contentType=colorscale />
  <Column id=forks_count title="Forks" />
  <Column id=activity_status title="Activity" />
  <Column id=popularity_tier title="Tier" />
</DataTable>

---

## 📈 Language Distribution

<BarChart 
  data={language_trends} 
  x=language 
  y=total_stars 
  title="Total Stars by Programming Language"
  type=grouped
/>

---

## 🔥 Trending Languages

<DataTable data={language_trends} rows=15>
  <Column id=language title="Language" />
  <Column id=repo_count title="Repos" />
  <Column id=total_stars title="Total Stars" />
  <Column id=avg_stars title="Avg Stars" />
  <Column id=avg_stars_per_day title="Avg Stars/Day" />
  <Column id=pct_of_total_stars title="% of Total" fmt=pct1 />
</DataTable>

---

## 📅 Repository Activity

<BarChart 
  data={repo_stats} 
  x=activity_status 
  y=repo_id 
  title="Repositories by Activity Status"
  labels=true
/>

---

*Last updated: {new Date().toLocaleDateString()}*
