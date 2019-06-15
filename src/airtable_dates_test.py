#!/usr/bin/env python3 -m pytest
from unittest.mock import patch, MagicMock, call
import airtable_dates as subject
from fixture_histobj import hist

def test_generate_final_states():
    "use recorded data"

    assert hist is not None

    # produce these two results in turn:
    fakehist = MagicMock()
    fakehist.get.side_effect = [True, hist]
    fakeclient = MagicMock()
    fakeclient.groups_history.return_value = fakehist

    gen = subject.generate_updates_for_states(fakeclient, ("Completed", "Not Us"), count=100)
    result = list(gen)
    fakeclient.groups_history.assert_called_once()

    # print(fakehist.get.call_args_list)
    fakehist.get.assert_any_call('ok')
    fakehist.get.assert_any_call('messages')
    assert len(result) == 4

    fup = result[0]
    assert fup.table == 'tblA4zbHiw2Lqyvzo'
    assert fup.record == 'recwr0jJXrmUqvNw5'
    assert fup.title == 'State'
    assert fup.newvalue == 'Completed'
    assert fup.timestamp == '1558674057.000400'


def test_generate_start_states():
    "use recorded data"

    assert hist is not None

    # produce these two results in turn:
    fakehist = MagicMock()
    fakehist.get.side_effect = [True, hist]
    fakeclient = MagicMock()
    fakeclient.groups_history.return_value = fakehist

    gen = subject.generate_updates_for_states(fakeclient, ("Started",), count=100)
    result = list(gen)
    fakeclient.groups_history.assert_called_once()

    # print(fakehist.get.call_args_list)
    fakehist.get.assert_any_call('ok')
    fakehist.get.assert_any_call('messages')
    assert len(result) == 3

    fup = result[0]
    assert fup.table == 'tblA4zbHiw2Lqyvzo'
    assert fup.record == 'rec42jUKrrdzvhZvQ'
    assert fup.title == 'State'
    assert fup.newvalue == 'Started'
    assert fup.timestamp == '1558737972.001000'




def test_airtable_update_completion():
    ""
    fake_updategen=[
        subject.FieldUpdate('State', 'Started', 'tblA4zbHiw2Lqyvzo', 'Rec', 1558737972),
        subject.FieldUpdate('State', 'Completed', 'tblA4zbHiw2Lqyvzo', 'Rec', 1552737972),
        subject.FieldUpdate('State', 'Completed', 'tblA4zbHiw2Lqyvzo', 'Rec', 1552737972),
    ]
    fakebase = MagicMock()
    fakebase.update.return_value('Rec')
    fakebase.get.side_effect = [
        {'id': 'Rec', 'fields': {'State': 'Started'}},
        {'id': 'Rec', 'fields': {'State': 'Completed'}},
        {'id': 'Rec', 'fields': {'State': 'Completed', 'Completion': '2019'}},
        ]

    subject.airtable_update_completion(fake_updategen, fakebase)

    print(fakebase.update.call_args_list)
    fakebase.update.assert_has_calls([
        call('Rec', {'Started': '2019-05-24' }),
        call('Rec', {'Completion': '2019-03-16' }),
        ], any_order=True)
    assert fakebase.update.call_count == 2


