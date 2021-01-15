
explain analyse
select count(*) from collection;
-- 2,295,588
-- 194ms
-- parallel seq scan

explain analyse
select count(*) from tumorpathologyevent;
-- 80,000
-- 30 ms

explain analyse
select * from collection order by label;
-- first 500 rows in 51ms
-- index scan collection_label_idx


select * from collection where type = 'Collection' order by id limit 500;


explain analyse
select * from collection where type = 'File' order by id limit 500;
-- 32ms
-- index scan collection_type_idx

explain analyse
select count(*) from collection where type = 'File';

select count(*) from collection
where type = 'File'
  and id like 'http://localhost:8080/api/webdav/collection%202020-11-16-2/%'
;

explain analyse
select * from collection
where type = 'File'
  and id like 'http://localhost:8080/api/webdav/collection%202020-11-16-2/%'
order by id
limit 500
;


explain analyse
select * from collection c where exists (
    select *
    from collection_sample cs
             join sample s on cs.sample_id = s.id
    where cs.collection_id = c.id
    and s.topography like '%a%'
)
and exists(
    select *
    from collection_analysistype ca
    where ca.collection_id = c.id
    and ca.analysistype = 'RNA-seq'
)
order by c.id
;
-- first 500 rows in 250ms

explain analyse
select count(*) from collection c
where exists (
    select *
    from collection_sample cs
             join sample s on cs.sample_id = s.id
    where cs.collection_id = c.id
      and s.topography like '%a%'
)
and exists(
    select *
    from collection_analysistype ca
    where ca.collection_id = c.id
      and ca.analysistype = 'RNA-seq'
)
;
-- 2,382
-- 228ms

select * from collection c
where exists (
        select *
        from collection_sample cs
                 join sample s on cs.sample_id = s.id
        where cs.collection_id = c.id
          and s.nature = 'RNA'
    )
  and exists(
        select *
        from collection_analysistype ca
        where ca.collection_id = c.id
          and ca.analysistype = 'RNA-seq'
    )
order by id limit 500
;

select count(*) from collection c
where exists (
        select *
        from collection_sample cs
                 join sample s on cs.sample_id = s.id
        where cs.collection_id = c.id
          and s.nature = 'RNA'
    )
  and exists(
        select *
        from collection_analysistype ca
        where ca.collection_id = c.id
          and ca.analysistype = 'RNA-seq'
    )
;

select * from sample
where nature = 'RNA'
order by id
limit 500;

select count(*) from sample
where nature = 'RNA';


select * from sample
where nature = 'RNA'
and tumorcellularity > 20
and tumorcellularity < 90
order by id
limit 500;

select count(*) from sample
where nature = 'RNA'
and tumorcellularity > 20
and tumorcellularity < 90;

explain analyse
select * from sample s
where nature = 'RNA'
  and exists (
      select * from sample_subject s_subj
      join subject subj on s_subj.subject_id = subj.id
      where subj.gender = 'Male'
      and s_subj.sample_id = s.id
    )
  and exists (
      select * from sample_tumorpathologyevent s_e
      join tumorpathologyevent e on s_e.tumorpathologyevent_id = e.id
      where e.eventtype = 'Neoplasm'
        and s_e.sample_id = s.id
    )
order by id
limit 500;

select count(*) from sample s
where nature = 'RNA'
  and exists (
        select * from sample_subject s_subj
            join subject subj on s_subj.subject_id = subj.id
        where subj.gender = 'Male'
          and s_subj.sample_id = s.id
    )
  and exists (
        select * from sample_tumorpathologyevent s_e
            join tumorpathologyevent e
                on s_e.tumorpathologyevent_id = e.id
        where e.eventtype = 'Neoplasm'
          and s_e.sample_id = s.id
    )
;


explain analyse
select * from collection c
where exists (
        select *
        from collection_sample cs
                 join sample s on cs.sample_id = s.id
        where cs.collection_id = c.id
          and s.nature = 'RNA'
    )
  and exists (
        select *
        from collection_subject csub
                 join subject sub on csub.subject_id = sub.id
        where csub.collection_id = c.id
          and sub.gender = 'Male'
    )
  and exists(
        select *
        from collection_analysistype ca
        where ca.collection_id = c.id
          and ca.analysistype = 'RNA-seq'
    )
order by c.id
;
-- 163 rows in 298ms

explain analyse
select count(*) from collection c
where exists (
        select *
        from collection_sample cs
                 join sample s on cs.sample_id = s.id
        where cs.collection_id = c.id
          and s.nature = 'RNA'
    )
  and exists (
        select *
        from collection_subject csub
                 join subject sub on csub.subject_id = sub.id
        where csub.collection_id = c.id
          and sub.gender = 'Male'
    )
  and exists(
        select *
        from collection_analysistype ca
        where ca.collection_id = c.id
          and ca.analysistype = 'RNA-seq'
    )
;
-- 163
-- 244ms

select * from sample s
where nature = 'RNA'
  and exists (
        select * from collection_sample cs
                          join collection_analysistype ca
                               on ca.collection_id = cs.collection_id
        where cs.sample_id = s.id
          and ca.analysistype = 'RNA-seq'
    )
  and exists (
        select * from sample_tumorpathologyevent s_e
                          join tumorpathologyevent e
                               on s_e.tumorpathologyevent_id = e.id
        where e.eventtype = 'Neoplasm'
          and s_e.sample_id = s.id
    )
order by id limit 500
;

select count(*) from sample s
where nature = 'RNA'
  and exists (
      select * from collection_sample cs
        join collection_analysistype ca
             on ca.collection_id = cs.collection_id
        where cs.sample_id = s.id
          and ca.analysistype = 'RNA-seq'
    )
  and exists (
        select * from sample_tumorpathologyevent s_e
          join tumorpathologyevent e
               on s_e.tumorpathologyevent_id = e.id
        where e.eventtype = 'Neoplasm'
          and s_e.sample_id = s.id
    )
;

explain analyse
select count(*) from collection c
where exists(
    select *
    from collection_keywords ck
    where ck.collection_id = c.id
      and ck.keywords = 'philosophy'
)
;
-- 161,065
-- 1s 66 ms

explain analyse
select count(*) from (
    select distinct ck.collection_id
    from collection_keywords ck
    where ck.keywords = 'philosophy'
) temp
;
-- 161,065
-- 300 ms

select distinct ck.collection_id
from collection_keywords ck
where ck.keywords = 'philosophy'
order by ck.collection_id
limit 500
;

explain analyse
select count(*)
from collection_sample cs
         join sample s on cs.sample_id = s.id
where s.tumorcellularity > 20 and s.tumorcellularity < 50;
-- 336,357
-- 260ms

explain analyse
select count(*)
from collection c
where c.id in (
    select cs.collection_id
    from collection_sample cs
    where cs.sample_id in (
        select s.id
        from sample s
        where s.tumorcellularity > 20
          and s.tumorcellularity < 40
    )
);
-- 146,984
-- 941ms

explain analyse
select count(*)
from collection c
where exists (
        select *
        from sample s
        join collection_sample cs on s.id = cs.sample_id
        where cs.collection_id = c.id
          and s.id = cs.sample_id
          and s.tumorcellularity > 20
          and s.tumorcellularity < 40
)
;
-- 146984 (907ms)

select cs.collection_id
from collection_sample cs
join sample s on cs.sample_id = s.id
where s.tumorcellularity > 20
  and s.tumorcellularity < 40
order by cs.collection_id
;
-- first 500 rows in 758ms

explain analyse
select count(distinct collection_id) from collection_sample
;
-- *:        746,206 (66ms)
-- total:    746,206 (88ms)
-- distinct: 615,497 (3.3s)

explain analyse
select count(*) from (select distinct collection_id from collection_sample) as temp;
-- 615,497 (510ms)

explain analyse
select count(*) from (select collection_id from collection_sample group by collection_id) as temp;
-- 615,497 (509ms)


explain analyse
select distinct collection_id from collection_sample
order by collection_id
;
-- first 500 rows in 26ms

select count(*)
from sample;

select *
from sample
order by id
limit 500;

explain analyse
select count(*)
from sample
where tumorcellularity > 50
  and tumorcellularity < 90
;
-- 75,328
-- 31ms

explain analyse
select count(*)
from (
         select distinct c.id
         from collection c
                  join collection_sample cs on cs.collection_id = c.id
                  join sample s on s.id = cs.sample_id
                  join collection_keywords ck on c.id = ck.collection_id
         where ck.keywords = 'philosophy'
           and s.tumorcellularity > 50
           and s.tumorcellularity < 90
     ) as temp
;
-- 25,045
-- 537ms

explain analyse
select count(*) from (
    select distinct cs.collection_id
    from collection_sample cs
        join sample s on s.id = cs.sample_id
        join collection_keywords ck on cs.collection_id = ck.collection_id
    where ck.keywords = 'philosophy'
      and s.tumorcellularity > 50
      and s.tumorcellularity < 90
    ) as temp;
-- 25,045
-- 373ms

explain analyse
select count(*) from (
    select ck.collection_id
    from collection_keywords ck
             join collection_sample cs on ck.collection_id = cs.collection_id
             join sample s on s.id = cs.sample_id
    where keywords = 'philosophy'
      and s.tumorcellularity > 30
      and s.tumorcellularity < 90
    order by ck.collection_id
) as temp
;
-- 28,137
-- 358ms


vacuum analyse;
-- 3s 44ms
