#include "searchable_tree_bag.hpp"
#include "searchable_array_bag.hpp"
#include "set.hpp"
#include <iostream>

int main()
{
	searchable_tree_bag tb;
	searchable_array_bag ab;
	int vals[] = {5, 3, 8, 3, -1, 5, 10, 0, -7, 8};
	tb.insert(vals, 10);
	ab.insert(vals, 10);
	tb.print();
	ab.print();
	for (int i = -8; i <= 11; i++)
		std::cout << i << ": " << tb.has(i) << " " << ab.has(i) << std::endl;

	searchable_tree_bag tb2(tb);
	searchable_array_bag ab2(ab);
	tb2.insert(42);
	ab2.insert(42);
	tb.print();
	tb2.print();
	ab.print();
	ab2.print();
	std::cout << tb.has(42) << tb2.has(42) << ab.has(42) << ab2.has(42) << std::endl;

	searchable_tree_bag tb3;
	searchable_array_bag ab3;
	tb3.insert(1);
	ab3.insert(1);
	tb3 = tb2;
	ab3 = ab2;
	tb2.clear();
	ab2.clear();
	tb3.print();
	ab3.print();
	tb2.print();
	ab2.print();
	std::cout << tb3.has(1) << ab3.has(1) << tb3.has(42) << ab3.has(42)
		<< tb2.has(42) << ab2.has(42) << std::endl;

	searchable_bag *bags[2] = {&tb3, &ab3};
	for (int i = 0; i < 2; i++)
	{
		bags[i]->insert(-100);
		std::cout << bags[i]->has(-100) << bags[i]->has(-99) << std::endl;
		bags[i]->print();
		bags[i]->clear();
		std::cout << bags[i]->has(-100) << std::endl;
		bags[i]->print();
	}

	const searchable_tree_bag ctb(tb);
	ctb.print();
	std::cout << ctb.has(10) << ctb.has(11) << std::endl;

	searchable_tree_bag tree_storage;
	set st(tree_storage);
	int dup[] = {4, 4, 2, 2, 9, 4, 1, 9};
	st.insert(dup, 8);
	st.insert(2);
	st.insert(7);
	st.print();
	st.get_bag().print();
	tree_storage.print();
	std::cout << st.has(4) << st.has(5) << st.has(7) << std::endl;
	st.clear();
	st.print();
	std::cout << st.has(4) << std::endl;
	st.insert(3);
	st.insert(3);
	st.print();

	searchable_array_bag array_storage;
	set sa(array_storage);
	for (int i = 0; i < 20; i++)
		sa.insert(i % 7);
	sa.insert(-3);
	sa.insert(-3);
	sa.print();
	const set &csa = sa;
	csa.print();
	std::cout << csa.has(3) << csa.has(7) << csa.has(-3) << std::endl;
	std::cout << csa.get_bag().has(6) << csa.get_bag().has(-4) << std::endl;
	csa.get_bag().print();
	return 0;
}
