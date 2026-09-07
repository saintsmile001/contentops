-- Creator profiles
create table if not exists public.creator_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users(id) on delete cascade,
  name text not null default '',
  description text not null default '',
  industry text not null default '',
  audience text not null default '',
  tone text not null default '',
  default_cta text not null default '',
  primary_platform text not null default 'linkedin',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.creator_profiles enable row level security;
create policy "Users manage their own profile" on public.creator_profiles
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Source contents
create table if not exists public.source_contents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  content text not null,
  file_url text,
  content_type text not null check (content_type in ('text', 'txt', 'md', 'pdf')),
  word_count integer not null check (word_count >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.source_contents enable row level security;

create policy "Users manage their own sources" on public.source_contents
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

insert into storage.buckets (id, name, public)
values ('source-files', 'source-files', false)
on conflict (id) do nothing;

create policy "Users upload their own source files" on storage.objects
  for insert to authenticated with check (
    bucket_id = 'source-files' and (storage.foldername(name))[1] = auth.uid()::text
  );

create table if not exists public.content_dna (
  id uuid primary key default gen_random_uuid(), source_id uuid not null unique references public.source_contents(id) on delete cascade,
  title text not null, main_thesis text not null, target_audience text not null, content_pillars jsonb not null default '[]', key_points jsonb not null default '[]', stories jsonb not null default '[]', claims jsonb not null default '[]', statistics jsonb not null default '[]', keywords jsonb not null default '[]', entities jsonb not null default '[]', tone text not null, cta text not null, summary text not null, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
alter table public.content_dna enable row level security;
create policy "Users manage DNA for their sources" on public.content_dna for all using (exists (select 1 from public.source_contents s where s.id = source_id and s.user_id = auth.uid())) with check (exists (select 1 from public.source_contents s where s.id = source_id and s.user_id = auth.uid()));

create table if not exists public.campaigns (id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade, source_id uuid not null references public.source_contents(id) on delete cascade, name text not null, duration integer not null default 7 check (duration = 7), platforms jsonb not null default '["linkedin", "x", "instagram"]', status text not null default 'DRAFT' check (status in ('DRAFT','GENERATING','COMPLETED','FAILED')), created_at timestamptz not null default now(), updated_at timestamptz not null default now());
alter table public.campaigns add column if not exists platforms jsonb not null default '["linkedin", "x", "instagram"]';
alter table public.campaigns enable row level security;
create policy "Users manage their campaigns" on public.campaigns for all using (auth.uid()=user_id) with check (auth.uid()=user_id);
create table if not exists public.campaign_strategies (id uuid primary key default gen_random_uuid(),campaign_id uuid not null unique references public.campaigns(id) on delete cascade,strategy jsonb not null,created_at timestamptz not null default now());
alter table public.campaign_strategies enable row level security;
create policy "Users manage their campaign strategies" on public.campaign_strategies for all using (exists(select 1 from public.campaigns c where c.id=campaign_id and c.user_id=auth.uid())) with check (exists(select 1 from public.campaigns c where c.id=campaign_id and c.user_id=auth.uid()));
create table if not exists public.content_assets (id uuid primary key default gen_random_uuid(),campaign_id uuid not null references public.campaigns(id) on delete cascade,platform text not null,content_type text not null,title text not null,hook text not null default '',content text not null,cta text not null default '',hashtags jsonb not null default '[]',scheduled_for timestamptz,status text not null default 'READY' check(status in ('GENERATING','READY','WARNING','FAILED')),created_at timestamptz not null default now(),updated_at timestamptz not null default now());
alter table public.content_assets enable row level security;
create policy "Users manage campaign assets" on public.content_assets for all using (exists(select 1 from public.campaigns c where c.id=campaign_id and c.user_id=auth.uid())) with check (exists(select 1 from public.campaigns c where c.id=campaign_id and c.user_id=auth.uid()));
create table if not exists public.qa_reports (id uuid primary key default gen_random_uuid(),asset_id uuid not null unique references public.content_assets(id) on delete cascade,faithfulness_score integer not null check(faithfulness_score between 0 and 100),source_coverage_score integer not null check(source_coverage_score between 0 and 100),brand_alignment_score integer not null check(brand_alignment_score between 0 and 100),unsupported_claims jsonb not null default '[]',supported_claims jsonb not null default '[]',issues jsonb not null default '[]',recommendations jsonb not null default '[]',status text not null check(status in ('PASS','WARNING','FAIL')),created_at timestamptz not null default now());
alter table public.qa_reports enable row level security;
create policy "Users manage asset QA" on public.qa_reports for all using(exists(select 1 from public.content_assets a join public.campaigns c on c.id=a.campaign_id where a.id=asset_id and c.user_id=auth.uid())) with check(exists(select 1 from public.content_assets a join public.campaigns c on c.id=a.campaign_id where a.id=asset_id and c.user_id=auth.uid()));
