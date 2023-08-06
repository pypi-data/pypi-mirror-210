# coding: utf8

import requests as r

from .aes import AESCipher
from .services import TRELLO_CREDENTIALS


class TrelloCard(object):
    """."""

    def __init__(self, board, list, card):
        """."""
        self.board_name = board.decode("utf8")
        self.list_name = list.decode("utf8")
        self.card_name = card.decode("utf8")
        self.params = {k: AESCipher().decrypt(v)
                       for (k, v) in TRELLO_CREDENTIALS}
        self.base_url = "https://trello.com/1/"
        self.__get_board_id()
        self.__get_list_id()
        self.__get_card_id()

    def __get_board_id(self):
        """."""
        url = self.base_url + "organizations/sisap1/boards"
        boards = {board["name"]: board["id"]
                  for board in r.get(url, params=self.params).json()}
        self.board_id = boards[self.board_name]
        url = self.base_url + "members/me"
        response = r.get(url, params=self.params).json()
        myself_id = response["id"]
        url = self.base_url + "boards/{}/members/{}".format(self.board_id,
                                                            myself_id)
        args = {"type": "normal"}
        response = r.put(url, params=self.params, data=args).json()  # noqa

    def __get_list_id(self):
        """."""
        url = self.base_url + "boards/{}/lists".format(self.board_id)
        lists = {list["name"]: list["id"]
                 for list in r.get(url, params=self.params).json()}
        if self.list_name in lists:
            self.list_id = lists[self.list_name]
        else:
            args = {"name": self.list_name}
            response = r.post(url, params=self.params, data=args).json()
            self.list_id = response["id"]

    def __get_card_id(self):
        """."""
        url = self.base_url + "lists/{}/cards".format(self.list_id)
        cards = {card["name"]: card["id"]
                 for card in r.get(url, params=self.params).json()}
        if self.card_name in cards:
            self.card_id = cards[self.card_name]
        else:
            url = self.base_url + "cards"
            args = {"name": self.card_name, "idList": self.list_id}
            response = r.post(url, params=self.params, data=args).json()
            self.card_id = response["id"]

    def __update_card(self, key, value):
        """."""
        url = self.base_url + "cards/{}".format(self.card_id)
        args = {key: value}
        response = r.put(url, params=self.params, data=args).json()  # noqa

    def add_description(self, text):
        """."""
        self.__update_card("desc", text)

    def add_members(self, *names):
        """."""
        url = self.base_url + "organizations/sisap1/members"
        all_members = {member["username"]: member["id"]
                       for member in r.get(url, params=self.params).json()}
        url = self.base_url + "boards/{}/members".format(self.board_id)
        board_members = [member["id"]
                         for member in r.get(url, params=self.params).json()]
        card_members = [all_members[name] for name in names]
        for member in card_members:
            if member not in board_members:
                url = self.base_url + "boards/{}/members/{}".format(
                                                                self.board_id,
                                                                member)
                args = {"type": "normal"}
                response = r.put(url, params=self.params, data=args)  # noqa
        self.__update_card("idMembers", card_members)

    def add_comment(self, text):
        """."""
        url = self.base_url + "cards/{}/actions/comments".format(self.card_id)
        args = {"text": text}
        response = r.post(url, params=self.params, data=args)  # noqa

    def add_to_checklist(self, checklist_name, item_name):
        """."""
        url = self.base_url + "cards/{}/checklists".format(self.card_id)
        checklists = {checklist["name"]: checklist["id"]
                      for checklist in r.get(url, params=self.params).json()}
        if checklist_name in checklists:
            checklist_id = checklists[checklist_name]
        else:
            args = {"name": checklist_name}
            response = r.post(url, params=self.params, data=args).json()
            checklist_id = response["id"]
        url = self.base_url + "checklists/{}/checkItems".format(checklist_id)
        items = {item["name"]: (item["id"], item["state"])
                 for item in r.get(url, params=self.params).json()}
        if item_name not in items:
            args = {"name": item_name}
            response = r.post(url, params=self.params, data=args).json()
        else:
            id, state = items[item_name]
            if state == "complete":
                s = "cards/{}/checklist/{}/checkItem/{}"
                url = self.base_url + s.format(self.card_id, checklist_id, id)
                args = {"state": "incomplete"}
                response = r.put(url, params=self.params, data=args)  # noqa
