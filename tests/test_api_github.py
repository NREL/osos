# -*- coding: utf-8 -*-
"""
Test for pypi API
"""
import datetime
import numpy as np
from osos.api_github.api_github import Github


def test_clones():
    """Test the github timeseries clone record"""
    gh = Github('NREL', 'reV')
    clones = gh.clones()
    for dt in clones.index.values:
        assert isinstance(dt, datetime.date)

    assert 'clones' in clones
    assert 'clones_unique' in clones
    assert clones['clones'].dtype == np.int64
    assert clones['clones_unique'].dtype == np.int64
    assert (clones['clones'] >= clones['clones_unique']).all()


def test_views():
    """Test the github timeseries view record"""
    gh = Github('NREL', 'reV')
    views = gh.views()
    for dt in views.index.values:
        assert isinstance(dt, datetime.date)

    assert 'views' in views
    assert 'views_unique' in views
    assert views['views'].dtype == np.int64
    assert views['views_unique'].dtype == np.int64
    assert (views['views'] >= views['views_unique']).all()


def test_issues_closed():
    """Test the github number of issues closed and lifetime"""
    gh = Github('NREL', 'reV')
    issues = gh.issues_closed(get_lifetimes=True)
    assert isinstance(issues['issues_closed'], list)
    assert isinstance(issues['issues_closed_count'], int)
    assert isinstance(issues['issues_closed_lifetimes'], list)
    assert isinstance(issues['issues_closed_mean_lifetime'], float)
    assert isinstance(issues['issues_closed_median_lifetime'], float)
    assert issues['issues_closed_count'] >= 146


def test_issues_open():
    """Test the github number of issues open and lifetime"""
    gh = Github('NREL', 'reV')
    issues = gh.issues_open(get_lifetimes=True)
    assert isinstance(issues['issues_open'], list)
    assert isinstance(issues['issues_open_count'], int)
    assert isinstance(issues['issues_open_lifetimes'], list)
    assert isinstance(issues['issues_open_mean_lifetime'], float)
    assert isinstance(issues['issues_open_median_lifetime'], float)


def test_pulls_open():
    """Test the github number of PR's open and lifetime"""
    gh = Github('NREL', 'reV')
    pulls = gh.pulls_open(get_lifetimes=True)
    assert isinstance(pulls['pulls_open'], list)
    assert isinstance(pulls['pulls_open_count'], int)
    assert isinstance(pulls['pulls_open_lifetimes'], list)
    assert isinstance(pulls['pulls_open_mean_lifetime'], float)
    assert isinstance(pulls['pulls_open_median_lifetime'], float)


def test_pulls_closed():
    """Test the github number of PR's closed and lifetime"""
    gh = Github('NREL', 'reV')
    pulls = gh.pulls_closed(get_lifetimes=True)
    assert isinstance(pulls['pulls_closed'], list)
    assert isinstance(pulls['pulls_closed_count'], int)
    assert isinstance(pulls['pulls_closed_lifetimes'], list)
    assert isinstance(pulls['pulls_closed_mean_lifetime'], float)
    assert isinstance(pulls['pulls_closed_median_lifetime'], float)
    assert pulls['pulls_closed_count'] >= 176


def test_forks():
    """Test the github number of forks"""
    gh = Github('NREL', 'reV')
    forks = gh.forks()
    assert isinstance(forks, int)
    assert forks >= 14


def test_stargazers():
    """Test the github number of stargazers"""
    gh = Github('NREL', 'reV')
    stargazers = gh.stargazers()
    assert isinstance(stargazers, int)
    assert stargazers >= 33


def test_subs():
    """Test the github number of subscribers"""
    gh = Github('NREL', 'reV')
    subs = gh.subscribers()
    assert isinstance(subs, int)
    assert subs >= 10


def test_contributors():
    """Test the github number of contributors"""
    gh = Github('NREL', 'reV')
    contributors = gh.contributors()
    print(contributors)
    assert isinstance(contributors, int)
    assert contributors >= 5


def test_commit_count():
    """Test the github total number of commits"""
    gh = Github('NREL', 'reV')
    count = gh.commit_count()
    assert isinstance(count, int)
    assert count >= 2217


def test_commit_record():
    """Test the github timeseries commit record"""
    d0 = datetime.date.today() - datetime.timedelta(days=14)
    gh = Github('NREL', 'reV')
    commits = gh.commits(date_start=d0)
    assert len(commits) == 15
    assert 'commits' in commits
    assert commits['commits'].dtype == np.int64
    assert all(commits['commits'] >= 0)
