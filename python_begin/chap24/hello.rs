
    fn maximal_suffix(arr: &[u8], reversed: bool) -> (uint, uint) {
        let mut left = -1; // Corresponds to i in the paper
        let mut right = 0; // Corresponds to j in the paper
        let mut offset = 1; // Corresponds to k in the paper
        let mut period = 1; // Corresponds to p in the paper

        while right + offset < arr.len() {
            let a;
            let b;
            if reversed {
                a = arr[left + offset];
                b = arr[right + offset];
            } else {
                a = arr[right + offset];
                b = arr[left + offset];
            }    
            if a < b {
                // Suffix is smaller, period is entire prefix so far.
                right += offset;
                offset = 1; 
                period = right - left;
            } else if a == b {
                // Advance through repetition of the current period.
                if offset == period {
                    right += offset;
                    offset = 1; 
                } else {
                    offset += 1;
                }    
            } else {
                // Suffix is larger, start over from current location.
                left = right;
                right += 1;
                offset = 1; 
                period = 1; 
            }    
        }    
        (left + 1, period)
    }

fn main(){

    let mut  z = [1u8,12,2,3,1,3,1,4,3,5,3,56,3,6,7,8,9];
    let mut k = maximal_suffix(&z, true);
    println!("{}", k);
}  
