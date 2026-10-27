#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct{
	int height, width;
	char free, ob, full;
	char **grid;
}t_map;

void free_map(t_map *map){
	if(!grid->map) return;
	for(int i = 0; i < map->height; i++){
		free(map->grid[i]);
	}
	free(map->grid);
	map->grid = NULL;
}

int notprint(int c){
	return(c < 32 || c > 126);
}
void print_map(t_map *map){
	for(int i = 0; i < map->height; i++){
		printf("%s\n",map->grid[i]);
	}
}

int read_map(FILE *file, t_map *map){
	size_t cap = 0;
	char *line = NULL;
	int len = getline(&line, &cap, file);
	if(len < 5 || line[len] != '\n') {free(line); return 1;}
	int i = 0; 
	map->height = 0; 
	while(i < len - 4 && line[i] >= '0'&& line[i]<= '9'){
		map->height = (map->height * 10) + line[i] - '0';
		i++;
	}
	if(i != len - 4){free(line); return 1;}
	map->free = line[i++];
	map->ob = line[i++];
	map->full = line[i++];
	if(height)return 1;
	map->grid = calloc(map->height, sizeof(char *));
	if(!map->grid){return 1;}
	map->width = 0;
	for(int i = 0; i < map->height; i++){
		int len = getline(&line, &cap, file);
		if(len < 2 || line[len - 1] != '\n') {free(line); return 1;}
		--len;
		if(i == 0) map->width = len;
		else if(map->width != len) {free(line); return 1;}
		for(int j = 0; j < map->width; j++){
			if(line[j] != map->free && line[j] != map->og){
				free(line);
				return 1;
			}
		}
		map->grid[i] = calloc(map->width + 1, sizeof(char));
		if(!map->grid[i]){free(line); return 1;}
		for(int j = 0 ;j < map->width; j++){
			map->grid[i][j] = line[j];
		}
		map->grid[i][map->width] = '\0';
	}
	free(line);
	return 1;
}

void solve(t_map *map){
	int *row = calloc(map->width, sizeof(int));
	int a = 0, b = 0, c = 0;
	for(int i = 0; i < map->height; i++){
		int diag = 0;
		for(int j = 0; j < map->width; j++){
			int top	= row[j];
			int size;
			if(map->grid[i][j] == map->ob) size = 0;
			else if(i == 0 || j == 0) size = 1;
			else{
				size = row[j - 1];
				if(top < size) size = top;
				if(diag < size) size = diag; 
				size++;
			}
			row[j] = size;
			diag = top;
			if(a < size){
				a = size; 
				b = i - size + 1;
				c = j - size + 1;
			}
		}
	}
	for(int i = b; i < b +a; i++){
		for(int j = c; j < c + a; j++){
			map->getline[i][j] = map->full;
		}
	}
	free(row);
}

void process(FILE *file){
	t_map map = {0};
	if(read_map(&map)){
		printf("Error: invalid map\n");
	}else{
		solve(&map);
		print_map(&map);
	}
	free_map(&map);
}

int main(int ac, char **av){
	if(ac == 1) process(stdin);
	else{
		FILE *file;
		for(int i = 1; i < ac; i++){
			file = fopen(av[i], "r");
			if(!file){printf("Error: invalid map\n"); continue;}
			process(file);
			fclose(file);
		}
	}
	return 0;
}