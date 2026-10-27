#pragma once
#include "tree_bag.hpp"
#include "searchable_bag.hpp"


class searchable_tree_bag : public tree_bag , public searchable_bag
{
	public:
		searchable_tree_bag(/* args */){}
		~searchable_tree_bag(){}
		searchable_tree_bag(const searchable_tree_bag &oth): tree_bag(oth){}
		searchable_tree_bag &operator=(const searchable_tree_bag &oth) {
				if (this != &oth)
					tree_bag::operator=(oth);
				return *this;
		}
		bool has(int val) const {
			node *current = tree;
			while (current)
			{
				if (val == current->value)
					return true;
				else if (val > current->value)
					current = current->r;
				else
					current  = current->l;
			}
			return false;
		}
};


