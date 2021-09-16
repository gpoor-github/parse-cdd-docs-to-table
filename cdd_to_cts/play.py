# test_rx_at_test_methods()
import rx
from rx import operators as ops

test_list = ["1 2 3", "4 5 6", "2 3 1"]
test_key: [int] = [0, 1, 2]
# rx.from_iterable(test_list).pipe(ops.to_dict(lambda key_seed: key_seed+'_key')).subscribe( lambda value: print("Received {0}".format(value)))
test_dic = dict((sub, test_list[sub]) for sub in test_key)
flat_dict_list = list((str(key) + test_dic[key]) for key in test_dic)
fd = sorted(test_dic.items(), key=lambda x: x[1], reverse=True)
rx.from_iterable(flat_dict_list).pipe(ops.map(lambda item: item)).subscribe(
    lambda value: print("Received {}".format(value)))
# , ops.combine_latest(lambda v: rx.from_iterable(list(v[0])),rx.from_iterable(test_list))
# rx.from_iterable(test_dic).subscribe( lambda value: print("Received {0"}.format(value)))
