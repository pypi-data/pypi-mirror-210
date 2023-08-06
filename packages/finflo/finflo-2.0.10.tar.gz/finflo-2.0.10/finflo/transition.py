import json
from .models import (
    SignList,
    TransitionManager,
    Action,
    workevents,
    workflowitems,
    Flowmodel,
)
from django.core import serializers as core_serializers
from .middleware import get_current_user
from .exception import (
    ModelNotFound,
    TransitionNotAllowed,
    ReturnModelNotFound,
)
from django.db.models import Q
from django.conf import settings
from collections import deque
from django.apps import apps
from django.forms.models import model_to_dict
from dataclasses import dataclass 
import contextlib 
from typing import Optional



####################################################
#############       CORE     #######################
####################################################



@dataclass
class FinFlotransition:

    # BASE CONSTRUCTORS #

    t_id : int or str
    model_type: str
    source: str
    destination: str
    interim: Optional[str] = None
    action : Optional[str] = None
    party : Optional[str] = None
    from_party: Optional[str] = None
    to_party : Optional[str] = None
    record_datas : Optional[None] = None


    def __post_init__(self):
        self.action = self.action.upper() if self.action else None
        gets_return_action = self.gets_default_return_action()
        if self.action:
            if self.action == self.gets_default_return_action().description:
                self.return_transition()
            else:
                self.transition()
        else:
            self.manualtransitions()
        

    def __repr__(self):
        return f"the id is {self.t_id} and type is {self.model_type}"

    def __str__(self):
        return f"the id is {self.t_id} and type is {self.model_type}"

    # GETS THE ALL MODEL VALUE FOR TRANSITION #

    def gets_base_action(self):
        try:
            return Action.objects.get(description=self.action, model__description=self.model_type)
        except:
            raise ModelNotFound()

    # RETURN ACTION
    def gets_default_return_action(self):
        try:
            return Action.objects.get(id=1)
        except:
            raise ReturnModelNotFound()

    # GETS WORKFLOW MODEL ID #
    def gets_wf_item(self, model):
        ws = workflowitems.objects.get(transitionmanager=model)
        return ws

    # GETS TRANSITION MANAGER
    def gets_base_model(self):
        try:
            return TransitionManager.objects.get(type=self.model_type, t_id=self.t_id)
        except Exception as e:
            raise ModelNotFound() from e

    def sign_reset(self, overall_model):
        overall_model[0].sub_sign = 0
        overall_model[0].in_progress = False
        overall_model[0].save()

    
    def get_record_datas(self):
        overall_model = self.gets_base_model()
        try:
            work_model = settings.FINFLO["WORK_MODEL"]
            for iter in work_model:
                gets_model = apps.get_model(iter)
                query_data = gets_model.objects.filter(id=overall_model.t_id)
                base_serialized_Data = core_serializers.serialize("json", query_data)
                if query_data.exists() and (gets_model._meta.db_table == overall_model.type):
                    break
                continue
            return {"values": json.loads(base_serialized_Data)}
        except Exception:
            return {"values": None}



    # GETS ALL ACTION
    def gets_all_models(self):
        try:
            gets_model = TransitionManager.objects.get(type__icontains=self.model_type, t_id=self.t_id)
            gets_flows = Flowmodel.objects.get(description__icontains=self.model_type)
            gets_action = Action.objects.get(
                Q(model=gets_flows.id) | Q(model=None),
                description=self.action,
                party=self.party or None,
            )
            gets_wf = self.gets_wf_item(gets_model.id)
            sign_lists = []
            try:
                for item in SignList.objects.all():
                    sign_lists.append(item.name)
                    if item.name == gets_action.stage_required.name:
                        break
                next_avail_trans = sign_lists[gets_model.sub_sign :]
                next_avail_trans_value = deque(next_avail_trans)
                next_avail_trans_value.popleft()
                next_avail_Transition = {"values": list(next_avail_trans_value)}
            except Exception:
                next_avail_Transition = None
            return (
                gets_model,
                gets_action,
                gets_flows,
                gets_wf,
                sign_lists,
                next_avail_Transition,
            )
        except:
            raise ModelNotFound()


    def return_transition(self):

        overall_model = self.gets_all_models()
        obj, created = workflowitems.objects.update_or_create(
            transitionmanager=overall_model[0] or overall_model[0].id,
            defaults={
                "initial_state": overall_model[1].from_state.description
                if overall_model[1].from_state
                else overall_model[3].initial_state,
                "interim_state": overall_model[1].to_state.description,
                "final_state": overall_model[1].to_state.description,
                "action": self.action,
                "record_datas": self.get_record_datas(),
                "subaction": self.action,
                "previous_action": overall_model[3].action,
                "next_available_transitions": None,
                "model_type": self.model_type,
                "event_user": get_current_user(),
                "final_value": True,
                "from_party": overall_model[1].from_party or self.from_party,
                "to_party": overall_model[1].to_party or self.to_party,
            },
        )
        workevents.objects.create(
            workflowitems=overall_model[3],
            event_user=get_current_user(),
            initial_state=overall_model[1].from_state.description
            if overall_model[1].from_state
            else overall_model[3].initial_state,
            final_value=True,
            record_datas=self.get_record_datas(),
            interim_state=overall_model[1].to_state.description,
            final_state=overall_model[1].to_state.description,
            action=self.action,
            subaction=self.action,
            model_type=self.model_type,
            from_party=overall_model[1].from_party or self.from_party,
            to_party=overall_model[1].to_party or self.to_party,
        )
        self.sign_reset(overall_model)

    




    # MANUAL TRANSITION WITH SOURCE , INTERIM , AND destination STATES

    def gets_default_model(self):
        obj , created = TransitionManager.objects.get_or_create(t_id =  self.t_id , type = self.model_type)
        return obj


    def manualtransitions(self):
        try:
            workflowitems.objects.filter(
                transitionmanager = self.gets_default_model()).update(
                initial_state =  self.source,
                interim_state =  self.interim,
                final_state =  self.destination,
                next_available_transitions = None,
                record_datas = self.record_datas,
                model_type = self.model_type,
                event_user =  get_current_user(),
                from_party = self.from_party,
                to_party = self.to_party,
                final_value = True,
            )
            workevents.objects.create(
            workflowitems = workflowitems.objects.get(transitionmanager = self.gets_default_model()),
            event_user=get_current_user(),
            initial_state=self.source,
            interim_state=self.interim,
            final_state=self.destination,
            model_type=self.model_type,
            record_datas=self.record_datas ,
            from_party=self.from_party,
            to_party=self.to_party,
            final_value=True,
            )
        except Exception:
            data = workflowitems.objects.create(
                transitionmanager = self.gets_default_model(),
                initial_state =  self.source,
                interim_state =  self.interim,
                final_state =  self.destination,
                next_available_transitions = None,
                record_datas = self.record_datas,
                model_type = self.model_type,
                event_user =  get_current_user(),
                from_party = self.from_party,
                to_party = self.to_party,
                final_value = True,
            )
            workevents.objects.create(
            workflowitems = data ,
            event_user=get_current_user(),
            initial_state=self.source,
            interim_state=self.interim,
            final_state=self.destination,
            model_type=self.model_type,
            record_datas=self.record_datas ,
            from_party=self.from_party,
            to_party=self.to_party,
            final_value=True,
            )
            # data = workflowitems.objects.get(transitionmanager = self.gets_default_model())

            
        # except Exception as e:
        #     raise TransitionNotAllowed() from e


    ## CORE TRANSITION ###

    def transition(self):

        overall_model = self.gets_all_models()

        if overall_model[0] is None:
            raise TransitionNotAllowed()
        try:
            ws = workflowitems.objects.update_or_create(
                transitionmanager=overall_model[0] or overall_model[0].id,
                defaults={
                    "initial_state": overall_model[1].from_state.description,
                    "interim_state": overall_model[4][
                        1 + overall_model[0].sub_sign
                    ],
                    "final_state": overall_model[1].to_state.description,
                    "next_available_transitions": overall_model[5],
                    "action": self.action,
                    "subaction": overall_model[4][overall_model[0].sub_sign],
                    "model_type": self.model_type,
                    "record_datas": self.get_record_datas(),
                    "event_user": get_current_user(),
                    "from_party": overall_model[1].from_party or self.from_party,
                    "to_party": overall_model[1].to_party or self.to_party,
                },
            )
            workevents.objects.create(
                workflowitems=overall_model[3],
                event_user=get_current_user(),
                initial_state=overall_model[1].from_state.description,
                interim_state=overall_model[4][1 + overall_model[0].sub_sign],
                record_datas=self.get_record_datas(),
                final_state=overall_model[1].to_state.description,
                action=self.action,
                subaction=self.action,
                model_type=self.model_type,
                from_party=overall_model[1].from_party or self.from_party,
                to_party=overall_model[1].to_party or self.to_party,
            )
            overall_model[0].sub_sign += 1
            overall_model[0].in_progress = True
            overall_model[0].save()
        except Exception:
            ws = workflowitems.objects.update_or_create(
                transitionmanager=overall_model[0] or overall_model[0].id,
                defaults={
                    "initial_state": overall_model[1].from_state.description,
                    "interim_state": overall_model[1].to_state.description,
                    "final_state": overall_model[1].to_state.description,
                    "action": self.action,
                    "next_available_transitions": None,
                    "subaction": self.action,
                    "model_type": self.model_type,
                    "record_datas": self.get_record_datas(),
                    "event_user": get_current_user(),
                    "from_party": overall_model[1].from_party or self.from_party,
                    "to_party": overall_model[1].to_party or self.to_party,
                    "final_value": True,
                },
            )
            workevents.objects.create(
                workflowitems=overall_model[3],
                event_user=get_current_user(),
                initial_state=overall_model[1].from_state.description,
                interim_state=overall_model[1].to_state.description,
                record_datas=self.get_record_datas(),
                final_state=overall_model[1].to_state.description,
                action=self.action,
                subaction=self.action,
                model_type=self.model_type,
                from_party=overall_model[1].from_party or self.from_party,
                to_party=overall_model[1].to_party or self.to_party,
                final_value=True,
            )
            # self.sign_reset(overall_model)
            overall_model[0].sign_reset

    
    



@dataclass
class DefaultModelValues:

    model_type : str
    id : str
    
    def get_record_Datas(self):
        try:
            gets_model = apps.get_model(self.model_type)
            query_data = gets_model.objects.filter(id=self.id)
            base_serialized_Data = core_serializers.serialize("json", query_data)
            if query_data.exists():
                return {"values": json.loads(base_serialized_Data)}
        except Exception:
            return {"values": None}