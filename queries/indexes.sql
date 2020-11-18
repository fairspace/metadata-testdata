drop index if exists subject_gender_idx;

drop index if exists event_topography_idx;
drop index if exists event_morphology_idx;
drop index if exists event_type_idx;

drop index if exists sample_topography_idx;
drop index if exists sample_origin_idx;
drop index if exists sample_nature_idx;
drop index if exists sample_tumorcellularity_idx;

drop index if exists collection_label_idx;
drop index if exists collection_type_idx;
drop index if exists keywords_collection_idx;

drop index if exists collection_subject_idx;
drop index if exists collection_event_idx;


create index if not exists subject_gender_idx on subject(gender);

create index if not exists event_topography_idx on tumorpathologyevent(topography);
create index if not exists event_morphology_idx on tumorpathologyevent(morphology);
create index if not exists event_type_idx on tumorpathologyevent(eventtype);

create index if not exists sample_topography_idx on sample(topography);
create index if not exists sample_origin_idx on sample(origin);
create index if not exists sample_nature_idx on sample(nature);
create index if not exists sample_tumorcellularity_idx on sample(tumorcellularity asc);

create index if not exists collection_label_idx on collection(label asc);
create index if not exists collection_type_idx on collection(type asc);
create index if not exists keywords_collection_idx on collection_keywords(keywords, collection_id);
create index if not exists analysis_collection_idx on collection_analysistype(analysistype, collection_id);

create index if not exists collection_subject_idx on collection_subject(collection_id, subject_id);
create index if not exists collection_event_idx on collection_tumorpathologyevent(collection_id, tumorpathologyevent_id);
