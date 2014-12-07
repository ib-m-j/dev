
create table main.deals (hash blob, deal text);
create unique index main.dealhash on deals(hash);
