#include <stdio.h>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <cstring>
#include <string>
#include <cmath>
#include <vector>
#include <set>
#include <map>
#include <queue>

using namespace std;

typedef long long ll;
typedef vector<int> vi;
typedef pair<int, int> ii;
typedef pair<pair<int, int>, int> iii;
typedef vector<ii> vii;
typedef set<int> si;
typedef map<string, int> msi;

#define I18F 1000000000000000000 // 10^18
#define INF 2000000000 // 2 billion
#define MEMSET_INF 127 // about 2B
#define MEMSET_HALF_INF 63 // about 1B

int GOAL_SCORE = 100;
bool debug = false;

int true_player = 0;

double Q[101][101][12];

int _S1 = 100;
int _S2 = 100;
int _A = 12;

ii s, s_p;
int a;
double epsilon = 1;
double alpha = 0.03;
double discount = 0.95;

int initialiseQTable(){
  for(int i = 0; i < _S1; ++i){
    for(int j = 0; j < _S2; ++j){
      for(int k = 0; k < _A; ++k){
        Q[i][j][k] = double(rand()) / double(RAND_MAX);
      }
    }
  }
}

double random_1(){ return (double(rand()) / double (RAND_MAX)); }

// act
int rl(int player_score, int opponent_score){
  s = make_pair(player_score, opponent_score);
  int best = 0;
  double best_val = Q[player_score][opponent_score][0];
  for(int i = 1; i < 12; ++i){
    if(Q[player_score][opponent_score][i] > best_val){
      best_val = Q[player_score][opponent_score][i];
      best = i;
    }
  }

  a = (random_1() < epsilon) ? rand() % 12 : best;
  epsilon -= 0.000000003;
  epsilon = max(epsilon, 0.005);
  return a - 1;
}

int s_max(int a, int b){
  int best = 0;
  double best_val = Q[a][b][0];
  for(int i = 1; i < 12; ++i){
    if(Q[a][b][i] > best_val){
      best_val = Q[a][b][i];
      best = i;
    }
  }
  return best - 1;
}

double s_p_max(){
  int best = 0;
  double best_val = Q[s_p.first][s_p.second][0];
  for(int i = 1; i < 12; ++i){
    if(Q[s_p.first][s_p.second][i] > best_val){
      best_val = Q[s_p.first][s_p.second][i];
      best = i;
    }
  }
  return best_val;
}

// learn 
int learn(int player_score, int opponent_score){
  double reward = 0;
  // profile 1
  //reward = (double) (player_score - opponent_score)/10;
  // profile 2
  //reward = (player_score > opponent_score)? 10 : -10;
  if(player_score >= GOAL_SCORE) reward = 500;
  if(opponent_score >= GOAL_SCORE) reward = -500;
  //printf("%d %d %d\n", player_score, opponent_score, reward);

  if(debug) printf("learning s: %d %d s': %d %d a: %d reward : %lf\n", s.first, s.second, s_p.first, s_p.second, a, reward);
  Q[s.first][s.second][a] += alpha * (reward + discount * s_p_max() - Q[s.first][s.second][a]);
}


int n_dice(int n){
  return (rand() % n) + 1;
}

int six_sided(){
  return n_dice(6);
}

int four_sided(){
  return n_dice(4);
}

int rerolled(int (&dice)()){
  int roll = dice();
  if(roll % 2 == 0) return roll;
  return dice();
}

int rerolled_4(){
  return rerolled(four_sided);
}

int rerolled_6(){
  return rerolled(six_sided);
}

int roll_dice(int num_rolls, int (&dice)() = six_sided){
  int pig_out = 0;
  int outcome = 0;
  for(int i = 0; i < num_rolls; ++i){
    int roll = dice();
    if(debug) printf(" %d ", roll);
    if(roll == 1) pig_out++;
    outcome += roll;
  }
  if(pig_out) return pig_out;
  return outcome;
}

int free_bacon(int opponent_score){
  return 1 + max(opponent_score/10, opponent_score%10);
}

bool is_prime(int x){
  if(x == 2) return true;
  if(x == 1 || x%2 == 0) return false;
  for(int i = 3; i < ceil(sqrt(x))+1; i+=2){
    if(x % i == 0) return false;
  }
  return true;
}

int next_prime(int x){
  if(x == 2) return 3;
  for(int i = x+2; i < 100; i+=2){
    if(is_prime(i)) return i;
  }
}

int next_primes[100];

int generate_primes(){
  next_primes[0] = 0;
  for(int i = 1; i < 100; ++i) next_primes[i] = (is_prime(i))?next_prime(i):i;
}

int take_turn(int num_rolls, int opponent_score, int (&dice)() = six_sided){
  int result;
  if(num_rolls == 0){
    result = free_bacon(opponent_score);
  }else{
    result = roll_dice(num_rolls, dice);
  }
  if(debug) printf("rolled %d ", result);
  
  result = next_primes[result];
  result = min(25 - num_rolls, result);
  return result;
}

int other(int player){ return 1 - player; }

ii play(int (&strategy0)(int, int), int (&strategy1)(int, int), int score0=0, int score1=0, int goal = GOAL_SCORE){
  int player = 0;
  bool dice_swapped = false; 

  while(score0 < goal && score1 < goal){
    int player_score = (player == 0) ? score0 : score1;
    int opponent_score = (player == 0) ? score1 : score0;

    int strategy = (player == 0) ? strategy0(player_score, opponent_score) : strategy1(player_score, opponent_score);

    int gain = 0;
    bool hog_wild = ((score0 + score1) % 7 == 0);
    
    if(debug) printf("player%d rolled %d dice ", player, strategy);
    if(strategy == -1){
      dice_swapped = !dice_swapped;
      gain = 1;
    }else{
      if(hog_wild){
        if(dice_swapped){
          gain = take_turn(strategy, opponent_score, rerolled_4);
        }else{
          gain = take_turn(strategy, opponent_score, rerolled_6);
        }
      }else{
        if(dice_swapped){
          gain = take_turn(strategy, opponent_score, four_sided);
        }else{
          gain = take_turn(strategy, opponent_score, six_sided);
        }
      }
    }
    
    if(debug) printf("and gained %d.\n", gain);

    if(player == 0) score0 += gain;
    if(player == 1) score1 += gain;
    
    if(max(score0,score1) == 2*min(score0,score1)){
      int store = score0;
      score0 = score1;
      score1 = store;
    }

    player = other(player);
    if(player == true_player || score0 >= GOAL_SCORE || score1 >= GOAL_SCORE){
      int true_score = (true_player == 0) ? score0 : score1;
      int other_score = score0 + score1 - true_score;
      true_score = min(100, true_score);
      other_score = min(100, other_score);
      s_p = make_pair(true_score, other_score);
      learn(true_score, other_score);
      s = s_p;
    }
    if(debug) printf("%d %d\n", score0, score1);
  }
  return make_pair(score0, score1);
}

int always_roll_random(int player_score, int opponent_score){
  int roll = rand() % 12 -1;
  return roll;
}

int always_roll_4(int player_score, int opponent_score){
  return 4;
}

int winner(int (&strategy0)(int, int), int (&strategy1)(int, int)){
  ii result = play(strategy0,strategy1);
  if(result.first > result.second) return 0;
  return 1;
}

float average_win_rate(int(&strategy0)(int,int), int(&strategy1)(int,int), int runs){
  int wins = 0;
  true_player = 0;
  for(int i = 0; i < runs/2; ++i) wins += 1 - winner(strategy0, strategy1);
  true_player = 1;
  for(int i = 0; i < runs/2; ++i) wins += winner(strategy1, strategy0);
  return float(wins)/float(runs);
}

int prime_bacon(int opponent_score){
  int result = free_bacon(opponent_score);
  if(is_prime(result)) result = next_prime(result);
  return result;
}

int swap_and_5(int player_score, int opponent_score){
  if(player_score == 0 || opponent_score == 0) return -1;
  int gain = prime_bacon(opponent_score);
  if((gain + player_score)*2 == opponent_score || gain >= 6) return 0;
  return 5;
}

int epochs = 1000000;

int rl_no_effect(int player_score, int opponent_score){
  return s_max(player_score, opponent_score);
}

void save_memory(){
  FILE * file;
  file = fopen("memory.txt", "w");
  fprintf(file, "[");
  for(int i = 0; i < 101; ++i){
    fprintf(file,"[");
    for(int j = 0; j < 101; ++j){
      fprintf(file, "%2d", s_max(i,j));
      if(j != 100){
        fprintf(file, ", ");
      }else{
        fprintf(file, "],");
      }
    }
    fprintf(file, "\n");
  }
  fprintf(file, "]");
  fclose(file);
}

int strategy[101][101];

void read_memory(){
  FILE * file;
  file = fopen("memory_clean.txt", "r");
  for(int i = 0; i < _S1; ++i){
    for(int j = 0; j < _S2; ++j){
      fscanf(file, "%d", &strategy[i][j]);
      if(i%5 == 0 && j % 5 == 0) printf("%d ", strategy[i][j]);
    }
    if(i % 5 == 0) printf("\n");
  }
  fclose(file);
}

void train_initial(){
  initialiseQTable();
  for(int i = 0; i < epochs; ++i){
    if(i%4 == 0){
        printf("epoch: %6d type: 4    epsilon: %lf winrate: %f\n", i + 1, epsilon, average_win_rate(rl, always_roll_4, 100000));
    }else if (i%4 == 1){
        printf("epoch: %6d type: rand epsilon: %lf winrate: %f\n", i + 1, epsilon, average_win_rate(rl, always_roll_random, 100000));
    }else if (i%4 == 2){
        printf("epoch: %6d type: rl   epsilon: %lf winrate: %f\n", i + 1, epsilon, average_win_rate(rl, rl_no_effect, 100000));
    }else if (i%4 == 3){
        printf("epoch: %6d type: s&5  epsilon: %lf winrate: %f\n", i + 1, epsilon, average_win_rate(rl, swap_and_5, 100000));
    }
    if(i % 100 == 0){
      for(int i = 0; i < 20; ++i){
        for(int j = 0; j < 20; ++j) printf("%2d ", s_max(i*5,j*5));
        printf("\n");
      }
      save_memory();
    }
  }
}

int final_strategy(int player_score, int opponent_score){
  return strategy[player_score][opponent_score];
}

void train_strategy(){
  initialiseQTable();
  for(int i = 0; i < epochs; ++i){
    printf("epoch: %6d type: final epsilon: %lf winrate: %f\n", i + 1, epsilon, average_win_rate(rl, final_strategy, 100000));
    if(i % 100 == 0){
      for(int i = 0; i < 20; ++i){
        for(int j = 0; j < 20; ++j) printf("%2d ", s_max(i*5,j*5));
        printf("\n");
      }
      save_memory();
    }
  }
}

int main(){
  srand(time(NULL));
  generate_primes();
  //read_memory();
  //train_strategy();
  train_initial();
  return 0;
}
