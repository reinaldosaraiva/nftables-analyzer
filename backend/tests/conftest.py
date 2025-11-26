"""Pytest fixtures for nftables-analyzer tests."""

import pytest

from nftables_analyzer.models.query import Query
from nftables_analyzer.models.rule import Rule


@pytest.fixture
def sample_rule_accept():
    """Sample accept rule for testing."""
    return Rule(
        action="accept",
        chain="input",
        table="filter",
        source="192.168.1.0/24",
        destination="10.0.0.5",
        sport="8080",
        dport="80",
        protocol="tcp",
        line_number=1,
        raw="tcp dport 80 accept",
    )


@pytest.fixture
def sample_rule_drop():
    """Sample drop rule for testing."""
    return Rule(
        action="drop",
        chain="input",
        table="filter",
        source="0.0.0.0/0",
        destination=None,
        sport=None,
        dport="22",
        protocol="tcp",
        line_number=2,
        raw="tcp dport 22 drop",
    )


@pytest.fixture
def sample_rules():
    """List of sample rules for testing."""
    return [
        Rule(
            action="accept",
            chain="input",
            table="filter",
            source="192.168.1.0/24",
            dport="80",
            protocol="tcp",
            line_number=1,
        ),
        Rule(
            action="drop",
            chain="input",
            table="filter",
            source="10.0.0.0/8",
            dport="22",
            protocol="tcp",
            line_number=2,
        ),
        Rule(
            action="accept",
            chain="output",
            table="filter",
            destination="8.8.8.8",
            protocol="udp",
            line_number=3,
        ),
    ]


@pytest.fixture
def sample_query():
    """Sample query for testing."""
    return Query(
        src_ip="192.168.1.10",
        dst_ip="10.0.0.5",
        src_port=8080,
        dst_port=80,
        protocol="tcp",
        direction="in",
    )
