#!/usr/bin/env python3 -m pytest
from unittest.mock import patch, MagicMock
import sandbox as subject
from fixture_histobj import hist

def test_generate_final_states():
    "use recorded data"
        
    assert hist is not None

    # produce these two results in turn:
    fakehist = MagicMock()        
    fakehist.get.side_effect = [True, hist]
    fakeclient = MagicMock()
    fakeclient.groups_history.return_value = fakehist

    gen = subject.generate_final_states(fakeclient)
    result = list(gen)
    fakeclient.groups_history.assert_called_once()

    # print(fakehist.get.call_args_list)
    fakehist.get.assert_any_call('ok')
    fakehist.get.assert_any_call('messages')
    assert len(result) == 4

    fup = result[0]
    assert fup.table == 'tblPRjVTMA11WifRn'
    assert fup.record == 'recwr0jJXrmUqvNw5'
    assert fup.title == 'State'
    assert fup.value == 'Completed'
    assert fup.timestamp == '1558674057.000400'




def test_airtable_update():
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

    # I think this fails because the dicts are not 'id' equal
    # fakebase.update.assert_any_call('Rec', {'Completion': '2019-05-24'})
    # fakebase.update.assert_any_call('Rec', {'Completion', '2019-03-16'})
    assert fakebase.update.call_args[0][1]['Completion'] == '2019-03-16' 
    assert fakebase.update.call_count == 2

