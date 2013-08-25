#!/usr/bin/perl -w

use strict;

package Account;
sub new {
    my $self = ();
    my $class = shift;

    $self->{"_value"} = shift;
    $self->{"_bids"} = [];
    $self->{"_asks"} = [];
    $self->{"_bidSize"} = 50;
    $self->{"_interval"} = 0.10;
    $self->{"_spread"} = 0.20;
    
    bless $self, $class;

    print "Starting value: $self->{_value}\n";

    return $self;
}
sub getValue {
    my( $self ) = @_;
    return $self->{_value};
}
sub setValue {
    my ($self, $value) = @_;
    $self->{_value} = $value if defined($value);
    return $self->{_value};
}
sub getAsks {
    my( $self ) = @_;
    return sort {$a <=> $b} @{$self->{_asks}};
}
sub getBids {
    my( $self ) = @_;
    return sort {$a <=> $b} @{$self->{_bids}};
}
sub bid {
    my( $self, $price ) = @_;
    $price = sprintf "%0.2f", $price;
    #print "bid $price\n";
    push @{$self->{_bids}}, $price;
}
sub ask {
    my( $self, $price ) = @_;
    $price = sprintf "%0.2f", $price;
    #print "ask $price\n";
    push @{$self->{_asks}}, $price
}
sub cancelBid {
    my( $self, $price ) = @_;
    my @bids = @{$self->{_bids}};
    $self->{_bids} = [];
    foreach my $bid (@bids) {
        if ($bid != $price) {
            $self->bid($bid);
        }
    }
}
sub cancelAsk {
    my( $self, $price ) = @_;
    my @asks = @{$self->{_asks}};
    $self->{_asks} = [];
    foreach my $ask (@asks) {
        if ($ask != $price) {
            $self->ask($ask);
        }
    }
}
sub insertBids {
    my $self = shift;
    my $ask = 0 + shift;
    my $bidSize = $self->{_bidSize};
    my $interval = $self->{_interval};
    
    my $capacity = $self->getValue();
   
    my $top = 0;
    my $bottom = $ask;
    foreach my $bid ($self->getBids()) {
        if( $top == 0 ) {
            $top = $bid;
            $bottom = $bid;
        } elsif ($bid > $top) {
            $top = $bid;
        } elsif ($bid < $bottom) {
            $bottom = $bid;
        }
        $capacity -= ($bidSize * $bid);
    }

    # Fill in bids as the price rises
    my $ceiling = $top;
    $ceiling += $interval;
    while ($ceiling < $ask) {
        $self->bid($ceiling);
        $ceiling += $interval;
        $capacity -= $bidSize * $ceiling;
    }

    # Fill in low bids, to capacity
    # TODO: Cancel bids that exceed capacity
    while ($capacity > 0) {
        $bottom -= $interval;
        my $cost = $bidSize * $bottom;
        if ($capacity > $cost) {
            $self->bid($bottom);
            $capacity -= $cost;
        } else {
            last;
        }
    }
}
sub tick {
    my ($self, $side, $price) = @_;
    my $bidSize = $self->{_bidSize};
    if ($side eq "ask") {
        $self->insertBids($price);
        foreach my $bid ($self->getBids()) {
            if ($price < $bid) {
                print "Executed bid at $bid...\n";
                $self->cancelBid($bid);
                $self->setValue($self->getValue() - ($bid*$bidSize));
                $self->ask($bid+$self->{_interval});
            }
        }
    } elsif ($side eq "bid") {
        foreach my $ask ($self->getAsks()) {
            if ($price > $ask) {
                print "Executed ask at $ask...\n";
                $self->setValue($self->getValue() + ($ask*$bidSize));
                $self->cancelAsk($ask);
            }
        }
    }
}

my $account = new Account(10000);

while (<>) {
    m/^([\d]+)\..*: \[(bid|ask), ([\d.]+)\]/;
    my ($timestamp, $side, $price) = ($1, $2, $3);
    $account->tick( $side, $price );
}

print $account->getValue() . "\n";
