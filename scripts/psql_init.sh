#!/usr/bin/env bash

if [ `psql postgres -tAc "SELECT 1 FROM pg_database WHERE datname='ymp3'"`0 -ne "10" ];
then
	psql -tAc "create database ymp3;" -q
	echo "Created DATABASE ymp3"
fi


if [ `psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='ymp3'"`0 -ne "10" ];
then
	psql -tAc "create user ymp3 with password 'ymp3';" -q
	echo "Created user ymp3"
fi

psql -tAc "grant all on database ymp3 to ymp3;" -q
